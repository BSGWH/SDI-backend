import os
from app.parsing_docs.service import parse_pdfs_in_folder
from anthropic import Anthropic
from fastapi import HTTPException
import asyncio
import re
import json

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("Missing ANTHROPIC_API_KEY")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

system_prompt = """You are a document validation assistant specializing in tenant ledger and lease documentation review. Your role is to carefully analyze provided documents and validate them against specific criteria.

IMPORTANT: Multiple documents may be combined within a single file. You must search for document titles, headers, or section markers within the provided files to identify each required document. Look for titles such as "Lease Agreement", "Lease Addendum", "Notification to Tenant", "Tenant Ledger", etc. within the content of the files.

When reviewing tenant ledger documents, you must:
 Verify the presence of all required and optional documents (whether as separate files OR as sections within combined files)

Required documents (may be separate files or sections within files):
- lease_addendum
- lease_agreement
- notification_to_tenant
- tenant_ledger

Optional documents (may be separate files or sections within files):
- invoice
- claim_evaluation_report

Document identification guidelines:
- Check file names AND content within files
- Look for document titles, headers, or clear section breaks
- A single file may contain multiple documents
- Document titles may appear as headers like "LEASE AGREEMENT", "Lease Addendum", "NOTIFICATION TO TENANT", etc.
- Consider variations in capitalization and formatting

Decision criteria:
- If any required file is missing (not found as a file OR within a file), set status to "Declined"
- To approve, ALL conditions must be met
- If any condition fails, set status to "Declined"

Always format your response as follows:
- Missing documents: [List of missing documents if applicable]
- Status: [Approved or Declined]"""

ledger_system_prompt = """You are a document validation assistant specializing in tenant ledger and lease documentation review. Your role is to carefully analyze provided documents and validate them against specific criteria.

IMPORTANT: Multiple documents may be combined within a single file. You must search for document titles, headers, or section markers within the provided files to identify each required document. Look for titles such as "Lease Agreement", "Lease Addendum", "Notification to Tenant", "Tenant Ledger", etc. within the content of the files.

When reviewing tenant ledger documents, you must:
1. Confirm that the rent for the first FULL month has been FULLY PAID by:
   - Identifying the first full month of tenancy (not partial/prorated month)
   - Calculating the NET rent due (after any concessions/credits)
   - Verifying that actual payments received equal or exceed the net amount due
   - Note: If payments are less than the amount due, this means NOT fully paid
   
2. Confirm that the first month's Security Deposit Insurance (SDI) premium has been COLLECTED by:
   - Identifying the SDI charge (may be labeled as "sd.pro", "SDI", "Security Deposit Protection", etc.)
   - Verifying that payment was received for this charge


Always format your response as follows:
- First FULL Month Paid: [True or False]
- First FULL Month Paid Evidence: [Insert the evidence of the First Month Paid]
- First Month SDI Premium Paid: [True or False]
- First Month SDI Premium Paid Evidence: [Insert the evidence of the First Month SDI Premium Paid]
"""

ledger_extraction_prompt = """You are a document extraction specialist. Your sole task is to locate and extract the tenant ledger from the provided files.

INSTRUCTIONS:
1. Search through all provided files to find the tenant ledger
2. The ledger may be:
   - A separate file named "tenant_ledger", "resident_ledger", "ledger", or similar
   - A section within a combined document with headers like "Tenant Ledger", "Resident Ledger", "Account Ledger", etc.
   - A table showing tenant charges, payments, and balances with transaction dates

3. CRITICAL FORMAT PRESERVATION RULES:
   - Extract the ENTIRE ledger exactly as it appears in the original
   - Preserve ALL formatting including:
     * Table structure and borders
     * Column headers and alignment
     * All rows and columns (even if empty)
     * Date formats
     * Number formats (including decimal places)
     * Any special characters or symbols
   - Do NOT summarize, reorganize, or reformat the data
   - Do NOT add interpretations or calculations
   - Include any header information above the ledger table (tenant name, property, dates, etc.)

4. Output ONLY the extracted ledger content, nothing else
   - No introductory text
   - No explanations
   - No analysis
   - Just the raw ledger data in its original format

If no ledger is found, respond only with: "NO LEDGER FOUND"

Remember: Your job is extraction only, not interpretation or validation."""


def mark_empty_cells(md_table: str, placeholder: str = "(empty)") -> str:
    """
    Replace empty markdown table cells with a placeholder.

    Example:
      "| foo |  | bar |"  ->  "| foo | (empty) | bar |"
    """
    lines = md_table.splitlines()
    out_lines = []

    for line in lines:
        # Only process table rows (those that start and end with |)
        if line.strip().startswith("|") and line.strip().endswith("|"):
            # Split on '|' but keep the delimiters
            parts = re.split(r"(\|)", line)
            # parts will look like: ["", "|", " foo ", "|", "   ", "|", " bar ", "|", ""]
            for i, part in enumerate(parts):
                # Only look at the cell content positions (i % 2 == 2, 4, 6, …)
                if i % 2 == 0:
                    # this is content; if blank or whitespace-only, replace
                    if part.strip() == "":
                        parts[i] = f" {placeholder} "
            out_lines.append("".join(parts))
        else:
            # leave non-table lines unchanged (headings, images, etc)
            out_lines.append(line)

    return "\n".join(out_lines)


#
async def checking_if_all_documents_available(fnames_and_files):
    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            system=ledger_system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Please review the attached files: {fnames_and_files}\n\n"
                    "Respond *only* in JSON matching this schema:\n"
                    "{\n"
                    '  "missing_documents": ["lease_agreement", ...],\n'
                    '  "status": "Approved"/"Declined",\n'
                    '  "reasons": ["...", "..."]\n'
                    "}",
                }
            ],
            max_tokens=2000,
        )

        raw = response.content

        if isinstance(raw, list):
            text = "".join(
                block.text if hasattr(block, "text") else str(block) for block in raw
            )
        else:
            text = raw.text if hasattr(raw, "text") else str(raw)

        parts = text.split("\n\n", 1)
        json_part = parts[0]
        comment_part = parts[1].strip() if len(parts) > 1 else ""
        data = json.loads(json_part)

        # Return both pieces
        return {
            "result": data,
            "commentary": comment_part,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def exact_only_leger_file(fnames_and_files):
    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            system=ledger_extraction_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Please review the attached files: {fnames_and_files}\n\n",
                }
            ],
            max_tokens=2000,
        )

        raw = response.content

        for block in raw:
            if hasattr(block, "text"):
                text = block.text
            else:
                text = str(block)

            if text.strip() == "NO LEDGER FOUND":
                return None

        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def check_first_month_rent_and_premium_paid(fnames_and_files):
    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Please review the attached files: {fnames_and_files}\n\n"
                    "Respond *only* in JSON matching this schema:\n"
                    "{\n"
                    '  "first_full_month_paid": true/false,\n'
                    '  "first_full_month_paid_evidence": "...",\n'
                    '  "first_month_sdi_premium_paid": true/false,\n'
                    '  "first_month_sdi_premium_paid_evidence": "...",\n'
                    "}",
                }
            ],
            max_tokens=2000,
        )

        raw = response.content
        if isinstance(raw, list):
            raw = "".join(
                block.text if hasattr(block, "text") else str(block) for block in raw
            )
        elif hasattr(raw, "text"):
            raw = raw.text

        print(raw)
        # print(type(raw))
        parsed = json.loads(raw)
        # print(parsed)
        # print(type(parsed))
        return parsed

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def decline_or_not(folder_path):
    # Parse all PDFs in the folder
    results = parse_pdfs_in_folder(folder_path)

    fnames_and_files = {}
    for fname, resp in results.items():
        if not resp:
            continue
        combined_md = "\n\n".join(
            mark_empty_cells(page.markdown) for page in resp.pages
        )
        fnames_and_files[fname] = combined_md
        print(combined_md)
    ledger_file = await exact_only_leger_file(fnames_and_files)
    # if_all_documents_available = await checking_if_all_documents_available(
    #     fnames_and_files
    # )

    # if if_all_documents_available["result"]["status"] == "Approved":
    #     return {
    #         "status": "Declined",
    #         "reasons": if_all_documents_available["result"]["reasons"],
    #     }
    # elif if_all_documents_available["result"]["status"] == "Declined":
    print("Ledger file:", ledger_file)
    return await check_first_month_rent_and_premium_paid(ledger_file)


if __name__ == "__main__":
    folder = "/Users/weihao/Library/CloudStorage/GoogleDrive-weihao.gu1994@gmail.com/.shortcut-targets-by-id/1-sEEs61X3q7AG8MV6y6wlX637KLOnMs4/all_docs/953"
    responses = asyncio.run(decline_or_not(folder))
