import os
from fastapi import FastAPI, HTTPException
from anthropic import Anthropic
from app.model import TrackingRequest
from dotenv import load_dotenv
from app.decline_decision.service import decline_or_not
from app.decline_decision.model import DeclineDecisionResponse
from fastapi.middleware.cors import CORSMiddleware
from app.parsing_docs.service import parse_pdfs_in_folder
from app.classify.service import classify_files
from app.classify_items.service import classify_items
from app.calculate_claim.service import calculate_claim
from app.read_csv.service import get_amount_of_claim
import pandas as pd

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("Missing ANTHROPIC_API_KEY")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/decline_or_not")
async def first_decision(req: TrackingRequest):
    print(req.tracking_number)
    folder = f"/Users/weihao/Library/CloudStorage/GoogleDrive-weihao.gu1994@gmail.com/.shortcut-targets-by-id/1-sEEs61X3q7AG8MV6y6wlX637KLOnMs4/all_docs/{req.tracking_number}"
    try:
        global classified_files
        parsed_files = parse_pdfs_in_folder(folder)
        classified_files = classify_files(parsed_files, client, req.tracking_number)
        print(f"Classified files: {classified_files}")
        result = await decline_or_not(classified_files)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calulate_amount")
async def sec_decision(req: TrackingRequest):
    try:
        if "Claim Evaluation Report" in classified_files.keys():
            claim_file = "\n".join(classified_files["Claim Evaluation Report"])
            print(f"Claim Evaluation Report: {claim_file}")
        else:
            claim_file = (
                "\n".join(classified_files["Tenant Ledger"])
                if "Tenant Ledger" in classified_files.keys()
                else ""
            )
        classified_items, max_benefit, rent = classify_items(
            claim_file, client, req.tracking_number
        )
        amount_of_claim = get_amount_of_claim(req.tracking_number)
        calculated_claim = calculate_claim(
            classified_items, max_benefit, rent, amount_of_claim
        )
        print(f"  -> Calculated claim: {calculated_claim}")
        return calculated_claim
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
