from typing import Dict, Any
import os
from anthropic import Anthropic
from collections import defaultdict
from app.read_csv.service import get_claim_amount


def classify_files(
    parsed_files: Dict[str, Any], client, tracking_number
) -> Dict[str, str]:
    # Define the valid classification categories
    claim_amount = get_claim_amount(tracking_number)
    print(f"Claim amount for tracking number {tracking_number}: {claim_amount}")
    valid_categories = [
        "Tenant Ledger",
        "Claim Evaluation Report",
        "Notification to Tenant",
        "Invoice",
        "Lease Addendum",
        "Lease Agreement",
        "Other",
    ]

    classified_files = defaultdict(list)

    for fname, content in parsed_files.items():
        print(f"Classifying file: {fname}")

        # Prepare the prompt for Claude
        prompt = f"""You are a document classification expert. Analyze the following document and classify it into exactly one of these categories:

Categories:
- Tenant Ledger (financial records showing tenant payment history, balances, charges, transaction logs, account statements, or any document with "ledger" in the filename)
- Claim Evaluation Report (assessment of damages, claims, or incidents can be named as "move out statement", "final statement" or similar, only add files that has the amount of {claim_amount}. IMPORTANT: If the document shows tenant payment history, transaction records, or account balances over time, classify it as "Tenant Ledger" instead, even if it contains the claim amount)
- Notification to Tenant (emails, notices, warnings, or communications to tenants)
- Invoice (bills, payment requests, or financial charges)
- Lease Addendum (modifications or additions to existing lease agreements)
- Lease Agreement (rental contracts or tenancy agreements)
- Other (any document that doesn't fit the above categories)

Document filename: {fname}

Document content:
{str(content)}

Based on the filename and content, respond with ONLY the category name from the list above. Do not include any explanation."""

        try:
            # Make the API call to Claude
            response = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=50,
                temperature=0,  # Set to 0 for most consistent classification
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract the classification from the response
            classification = response.content[0].text.strip()
            print(f"  -> Claude response: {classification}")

            # Validate the classification
            if classification not in valid_categories:
                print(
                    f"Warning: Invalid classification '{classification}' for {fname}. Defaulting to 'Other'"
                )
                classification = "Other"

            classified_files[classification].append(parsed_files[fname])
            # classified_files[classification].append(fname)

            # # Special handling for "Tenant Ledger" and "Claim Evaluation Report"
            # if "Claim Evaluation Report" in classified_files:
            #     ledger_files = [
            #         f
            #         for f in classified_files["Claim Evaluation Report"]
            #         if "ledger" in f.lower()
            #     ]
            #     if ledger_files:
            #         classified_files["Tenant Ledger"].extend(ledger_files)
            #         classified_files["Claim Evaluation Report"] = [
            #             f
            #             for f in classified_files["Claim Evaluation Report"]
            #             if "ledger" not in f.lower()
            #         ]
            print(f"  -> Classified as: {classification}")
            print(classified_files)

        except Exception as e:
            print(f"Error classifying {fname}: {str(e)}. Defaulting to 'Other'")
            classified_files[fname] = "Other"

    return classified_files
