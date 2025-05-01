import base64
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Union
from g4f.client import AsyncClient
from extract_text import extract_text_from_base64

# Initialize FastAPI
app = FastAPI()

# Healthcheck route
@app.get("/")
def root():
    return {"message": "Server is awake!"}

class RequestPayload(BaseModel):
    prompt: str
    model: str
    provider: Optional[str] = None
    image_base64: Optional[str] = None  # only 1 image allowed
    file_base64: Optional[Union[str, List[str]]] = None
    use_search: Optional[bool] = False
    image_format: Optional[str] = "b64_json"

@app.post("/g4f")
async def g4f_endpoint(payload: RequestPayload):
    model = payload.model
    requested_provider = payload.provider

    providers_to_try = [requested_provider] if requested_provider else []
    providers_to_try.append(None)  # fallback to RetryProvider

    last_exception = None

    for current_provider in providers_to_try:
        try:
            if current_provider:
                print(f"Trying with provider: {current_provider}")
                client = AsyncClient(provider=current_provider)
            else:
                print("Trying with fallback RetryProvider...")
                client = AsyncClient()

            # Special handling for image generation models
            if model in ["flux", "dall-e-3", "midjourney"]:
                if payload.prompt:
                    result = await client.images.generate(
                        prompt=payload.prompt,
                        model=model,
                        response_format=payload.image_format
                    )
                    return {"image_base64": result.data[0].b64_json} if payload.image_format == "b64_json" else {"url": result.data[0].url}
                return {"error": "Prompt required for image generation."}

            # Prepare chat messages
            messages = [{"role": "user", "content": payload.prompt}]
            image = None

            # Handle 1 image upload for vision models
            if payload.image_base64:
                image_bytes = base64.b64decode(payload.image_base64)
                image = image_bytes

            # Handle multiple file uploads and extract text
            if payload.file_base64:
                if isinstance(payload.file_base64, str):
                    payload.file_base64 = [payload.file_base64]

                combined_texts = []
                for file_b64 in payload.file_base64:
                    extracted_text = extract_text_from_base64(file_b64)
                    if extracted_text:
                        combined_texts.append(extracted_text.strip())

                if combined_texts:
                    combined_text = "\n\n".join(combined_texts)
                    messages[0]["content"] += "\n\n[Content Extracted From Attached Files Below]\n" + combined_text
            print(messages[0]["content"])
            # Optional search tool
            tool_calls = [
                {
                    "function": {
                        "name": "search_tool",
                        "arguments": {
                            "query": payload.prompt,
                            "max_results": 5,
                            "max_words": 2000,
                            "add_text": True,
                            "timeout": 5
                        }
                    },
                    "type": "function"
                }
            ] if payload.use_search else None

            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                image=image,
                tool_calls=tool_calls
            )
            return {"message": response.choices[0].message.content}

        except Exception as e:
            print(f"Provider {current_provider if current_provider else 'RetryProvider'} failed: {str(e)}")
            last_exception = e

    return {"error": f"All providers failed: {str(last_exception)}"}