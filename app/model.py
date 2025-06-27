from pydantic import BaseModel


class MessageRequest(BaseModel):
    prompt: str
    max_tokens: int = 256
