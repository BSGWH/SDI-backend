from pydantic import BaseModel


class TrackingRequest(BaseModel):
    tracking_number: str
