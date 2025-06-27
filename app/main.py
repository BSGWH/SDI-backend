import os
from fastapi import FastAPI, HTTPException
from anthropic import Anthropic
from app.model import MessageRequest


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("Missing ANTHROPIC_API_KEY")

client = Anthropic(api_key=ANTHROPIC_API_KEY)
app = FastAPI(title="Anthropic Chat Service")


@app.post("/chat")
async def chat(req: MessageRequest):
    """
    Send a user prompt via the new messages.create API.
    """
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            messages=[{"role": "user", "content": req.prompt}],
            max_tokens=req.max_tokens,
        )
        # extract the assistant’s reply
        reply = response.content
        return {"output": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
