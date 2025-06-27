import os
from fastapi import FastAPI, HTTPException
from anthropic import Anthropic
from app.model import TrackingRequest
from dotenv import load_dotenv
from app.decline_decision.service import decline_or_not
from app.decline_decision.model import DeclineDecisionResponse

load_dotenv()

# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
# if not ANTHROPIC_API_KEY:
#     raise RuntimeError("Missing ANTHROPIC_API_KEY")

# client = Anthropic(api_key=ANTHROPIC_API_KEY)
app = FastAPI()


@app.post("/decline_or_not")
async def first_decision(req: TrackingRequest):
    print(req.tracking_number)
    folder = f"/Users/weihao/Library/CloudStorage/GoogleDrive-weihao.gu1994@gmail.com/.shortcut-targets-by-id/1-sEEs61X3q7AG8MV6y6wlX637KLOnMs4/all_docs/{req.tracking_number}"
    try:
        result = await decline_or_not(folder)
        return result
    except Exception as e:
        # bubble up as HTTP 500
        raise HTTPException(status_code=500, detail=str(e))
