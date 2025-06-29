import pandas as pd
from fastapi import FastAPI, HTTPException

path = "/Users/weihao/Downloads/Security Deposit Claims.csv"


def get_claim_amount(tracking_number: str):
    print(f"Getting amount for tracking number: {tracking_number}")
    # here is where you give pandas the path
    df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")

    df.columns = df.columns.str.strip().str.replace("\ufeff", "")
    df["Tracking Number"] = df["Tracking Number"].astype(str)
    matched = df.loc[df["Tracking Number"] == tracking_number, "Amount of Claim"]
    if matched.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No claim found for tracking number {tracking_number}",
        )

    raw = matched.iloc[0]
    try:
        cleaned = str(raw).replace("$", "").replace(",", "")
        return float(cleaned)
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail=f"Could not parse claim amount '{raw}' for {tracking_number}",
        )


def get_max_benefit(tracking_number: str):
    print(f"Getting max benefit for tracking number: {tracking_number}")
    # here is where you give pandas the path
    df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")

    df.columns = df.columns.str.strip().str.replace("\ufeff", "")
    df["Tracking Number"] = df["Tracking Number"].astype(str)
    matched = df.loc[df["Tracking Number"] == tracking_number, "Max Benefit"]
    if matched.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No max benefit found for tracking number {tracking_number}",
        )

    raw = matched.iloc[0]
    try:
        cleaned = str(raw).replace("$", "").replace(",", "")
        return float(cleaned)
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail=f"Could not parse max benefit '{raw}' for {tracking_number}",
        )


def get_rent(tracking_number: str):
    print(f"Getting rent for tracking number: {tracking_number}")
    # here is where you give pandas the path
    df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")

    df.columns = df.columns.str.strip().str.replace("\ufeff", "")
    df["Tracking Number"] = df["Tracking Number"].astype(str)
    matched = df.loc[df["Tracking Number"] == tracking_number, "Monthly Rent"]
    if matched.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No rent found for tracking number {tracking_number}",
        )

    raw = matched.iloc[0]
    try:
        cleaned = str(raw).replace("$", "").replace(",", "")
        return float(cleaned)
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail=f"Could not parse rent '{raw}' for {tracking_number}",
        )


def get_amount_of_claim(tracking_number: str):
    print(f"Getting amount of claim for tracking number: {tracking_number}")
    # here is where you give pandas the path
    df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")

    df.columns = df.columns.str.strip().str.replace("\ufeff", "")
    df["Tracking Number"] = df["Tracking Number"].astype(str)
    matched = df.loc[df["Tracking Number"] == tracking_number, "Amount of Claim"]
    if matched.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No amount of claim found for tracking number {tracking_number}",
        )

    raw = matched.iloc[0]
    try:
        cleaned = str(raw).replace("$", "").replace(",", "")
        return float(cleaned)
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail=f"Could not parse amount of claim '{raw}' for {tracking_number}",
        )


if __name__ == "__main__":
    print(get_claim_amount("811"))

    print(get_max_benefit("811"))
    print(get_rent("811"))
    print(get_amount_of_claim("811"))
