from pydantic import BaseModel
from typing import List


class DeclineDecisionResponse(BaseModel):
    first_full_month_paid: bool
    first_full_month_paid_evidence: str
    first_month_sdi_premium_paid: bool
    first_month_sdi_premium_paid_evidence: str
    missing_documents: List[str]
    status: str
    reasons: List[str]
