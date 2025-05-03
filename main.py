import base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Union, Literal, Dict, Any
from g4f.client import AsyncClient
from extract_text import extract_text_from_base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Server is awake!"}

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class RequestPayload(BaseModel):
    prompt: Optional[str] = None
    model: str
    provider: Optional[str] = None
    image_base64: Optional[str] = None
    file_base64: Optional[Union[str, List[str]]] = None
    use_search: Optional[bool] = False
    image_format: Optional[str] = "b64_json"
    messages: Optional[List[Message]] = None

@app.post("/g4f")
async def g4f_endpoint(payload: RequestPayload):
    model = payload.model
    requested_provider = payload.provider

    providers_to_try = [requested_provider] if requested_provider else []
    providers_to_try.append(None)

    last_exception = None

    for current_provider in providers_to_try:
        try:
            if current_provider:
                print(f"Trying with provider: {current_provider}")
                client = AsyncClient(provider=current_provider)
            else:
                print("Trying with fallback RetryProvider...")
                client = AsyncClient()

            messages = [msg.dict() for msg in payload.messages] if payload.messages else [{"role": "user", "content": payload.prompt or ""}]

            if model in ["flux", "dall-e-3", "midjourney"]:
                if messages:
                    result = await client.images.generate(
                        prompt=messages[-1]["content"],
                        model=model,
                        response_format=payload.image_format
                    )
                    return {"image_base64": result.data[0].b64_json} if payload.image_format == "b64_json" else {"url": result.data[0].url}
                return {"error": "Prompt or messages required for image generation."}

            image = None

            if payload.image_base64:
                image_bytes = base64.b64decode(payload.image_base64)
                image = image_bytes

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
                    messages[-1]["content"] += "\n\n[Content Extracted From Attached Files Below]\n" + combined_text
            print(messages[-1]["content"])

            tool_calls = [
                {
                    "function": {
                        "name": "search_tool",
                        "arguments": {
                            "query": payload.prompt or messages[-1]["content"],
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