from app.classify_items.utils import STANDARD_CATEGORIES
from app.read_csv.service import get_max_benefit, get_rent
from app.calculate_claim.service import calculate_claim
import re
import json
import math


def keep_all_pairs(pairs):
    """
    pairs: a list of (key, value) tuples in the exact order they appeared in the JSON.
    We simply return it directly so json.loads doesn’t collapse duplicates.
    """
    return pairs


def classify_items(claim_file: str, client, is_ledger, tracking_number):
    max_benefit = get_max_benefit(tracking_number)
    rent = get_rent(tracking_number)
    if not max_benefit:
        max_benefit = math.ceil(rent / 500) * 500

    categories_list = "\n".join(
        [f"- {key}: {desc}" for key, desc in STANDARD_CATEGORIES.items()]
    )
    if is_ledger:
        print("******Classifying items in ledger*******")
        prompt = f"""You are a Security Deposit Insurance (SDI) claim analyzer. Your task is to analyze tenant charges and categorize them according to policy coverage guidelines.

This is the files to review: {claim_file}, if the input file is a ledger, you should only analyze the charges that are not paid or overdue that sum up to the {max_benefit}.

## Your Role:
Analyze each charge from a security deposit statement and categorize it. You must strictly follow the policy guidelines.

## Critical Instructions:
- Output ONLY a valid JSON structure - no additional text, explanations, or notes
- Do NOT include any text before or after the JSON
- Do NOT add categories like "credits" that aren't in the specified format


## Your Task:
For each charge:
1. Assign it to ONE of these standard categories:
{categories_list}

2. Provide a brief description of what the charge is for

## Required Output Format:
{{
  "actual_item_name_from_document": {{
    "amount": 0.00,
    "category": "CATEGORY_CODE",
    "reasoning": "Brief description of what this charge is for"
  }},
  "another_item_name": {{
    "amount": 0.00,
    "category": "CATEGORY_CODE", 
    "reasoning": "Brief description of what this charge is for"
  }}
}}

## Important:
- Use the EXACT category codes (e.g., "CLEANING", "CARPET", "LANDSCAPING")
- Every item MUST have a category
- Use "OTHER" only if no category fits
- Use the exact item names as they appear in the document
- If you cannot find the amount for an item, do not make assumptions, just skip it


Note: The number of items in each category will vary based on the actual charges in the security deposit statement. Use the exact item names from the document.

## Analysis Guidelines:

### General Rules:
1. The Final Payout Based on Coverage should not exceed the Maximum Benefit specified in the input data.
2. If an item or group of items is classified as "Beyond normal wear and tear," no further individual analysis is needed - mark it as covered.
3. Only consider charges/transactions that have not been paid or are overdue.
4. Only use charges/transactions explicitly stated in the documents - do not make assumptions or add items.
5. If charges are bundled without individual amounts, treat them as a single item.

### Coverage Inclusions:
- Cleaning charges for excessive dirt, damage, or stains beyond normal wear and tear
- Move-out rekey costs
- Landscaping repairs (including dead or missing plants)
- Unpaid utilities
- Lease break fee equal to one month's rent (excess not covered)
- Unpaid rent not exceeding one month's rent

### Coverage Exclusions/Limitations:
- Lease Break/Relisting Fees exceeding one month's rent (unless linked to accelerated move-out)
- Other Tenant Benefit Programs and Services
- Normal wear and tear

- Pet damage
- Prorated Rent (unless directly linked to tenant's occupancy/lease obligations for partial rental income recovery)
- Non-Refundable Fees

### Normal Wear and Tear:
- Fading, peeling, or cracked paint
- Slightly torn or faded wallpaper
- Small chips in plaster
- Nail holes, pin holes, or cracks in walls
- Door sticking from humidity
- Cracked window pane from faulty foundation or building settling
- Floors needing a coat of varnish
- Carpet faded or worn thin from walking
- Loose grouting and bathroom tiles
- Worn or scratched enamel in old bathtubs, sinks, or toilets
- Rusty shower rod
- Partially clogged sinks from aging pipes
- Dirty or faded lamp or window shades

### Tenant Damage Beyond Normal Wear and Tear:
- Gaping holes in walls or plaster
- Drawings, crayon markings, or unapproved wallpaper
- Seriously damaged or ruined wallpaper
- Chipped or gouged wood floors
- Doors ripped off hinges
- Broken windows
- Missing fixtures
- Holes in ceiling from removed fixtures
- Holes, stains, or burns in carpet
- Missing or cracked bathroom tiles
- Chipped and broken enamel in bathtubs and sinks
- Clogged or damaged toilets from improper use
- Missing or bent shower rods
- Torn, stained, or missing lamp and window shades

## Important Notes:
- Always provide specific reasoning referencing the policy guidelines
- Be precise with amounts - use the exact figures from the document
- When monthly rent amount is needed for lease break or unpaid rent calculations, it must be provided in the input data
Output the JSON classification now:"""

    else:
        print("******Classifying items in claim files*******")
        prompt = f"""You are a Security Deposit Insurance (SDI) claim analyzer. "Your task is to analyze all tenant transactions (both charges and credits) and categorize them"
This is the files to review: {claim_file}
## Your Role:
Analyze each transaction from a security deposit statement and categorize it. You must strictly follow the policy guidelines.

## Critical Instructions:
- Output ONLY a valid JSON structure - no additional text, explanations, or notes
- Do NOT include any text before or after the JSON


## Your Task:
For each transaction (charge or credit):
1. Assign it to ONE of these standard categories:
{categories_list}

2. Provide a brief description of what the charge is for

## Required Output Format:
{{
  "actual_item_name_from_document": {{
    "amount": 0.00,
    "category": "CATEGORY_CODE",
    "reasoning": "Brief description of what this charge is for"
  }},
  "another_item_name": {{
    "amount": 0.00,
    "category": "CATEGORY_CODE", 
    "reasoning": "Brief description of what this charge is for"
  }}
}}

## Important:
- Use the EXACT category codes (e.g., "CLEANING", "CARPET", "LANDSCAPING")
- Every item MUST have a category
- Use "OTHER" only if no category fits
- Use the exact item names as they appear in the document
- If you cannot find the amount for an item, do not make assumptions, just skip it


Note: The number of items in each category will vary based on the actual charges in the security deposit statement. Use the exact item names from the document.

## Analysis Guidelines:

### General Rules:
1. The Final Payout Based on Coverage should not exceed the Maximum Benefit specified in the input data.
2. If an item or group of items is classified as "Beyond normal wear and tear," no further individual analysis is needed - mark it as covered.

3. Only use charges/transactions explicitly stated in the documents - do not make assumptions or add items.
4. If charges are bundled without individual amounts, treat them as a single item.

### Coverage Inclusions:
- Cleaning charges for excessive dirt, damage, or stains beyond normal wear and tear
- Move-out rekey costs
- Landscaping repairs (including dead or missing plants)
- Unpaid utilities
- Lease break fee equal to one month's rent (excess not covered)
- Unpaid rent not exceeding one month's rent

### Coverage Exclusions/Limitations:
- Lease Break/Relisting Fees exceeding one month's rent (unless linked to accelerated move-out)
- Other Tenant Benefit Programs and Services
- Normal wear and tear

- Pet damage
- Prorated Rent (unless directly linked to tenant's occupancy/lease obligations for partial rental income recovery)
- Non-Refundable Fees

### Normal Wear and Tear:
- Fading, peeling, or cracked paint
- Slightly torn or faded wallpaper
- Small chips in plaster
- Nail holes, pin holes, or cracks in walls
- Door sticking from humidity
- Cracked window pane from faulty foundation or building settling
- Floors needing a coat of varnish
- Carpet faded or worn thin from walking
- Loose grouting and bathroom tiles
- Worn or scratched enamel in old bathtubs, sinks, or toilets
- Rusty shower rod
- Partially clogged sinks from aging pipes
- Dirty or faded lamp or window shades

### Tenant Damage Beyond Normal Wear and Tear:
- Gaping holes in walls or plaster
- Drawings, crayon markings, or unapproved wallpaper
- Seriously damaged or ruined wallpaper
- Chipped or gouged wood floors
- Doors ripped off hinges
- Broken windows
- Missing fixtures
- Holes in ceiling from removed fixtures
- Holes, stains, or burns in carpet
- Missing or cracked bathroom tiles
- Chipped and broken enamel in bathtubs and sinks
- Clogged or damaged toilets from improper use
- Missing or bent shower rods
- Torn, stained, or missing lamp and window shades

## Important Notes:
- Always provide specific reasoning referencing the policy guidelines
- Be precise with amounts - use the exact figures from the document
- When monthly rent amount is needed for lease break or unpaid rent calculations, it must be provided in the input data
Output the JSON classification now:"""

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=2000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract the classification from the response
        classification_resp = response.content[0].text.strip()
        print(f"  -> Claude response: {classification_resp}")
        # Find the JSON block and parse it
        match = re.search(r"\{.*\}", classification_resp, re.DOTALL)
        if match:
            json_str = match.group(0)
            parsed_classification = json.loads(json_str)
            # parsed_classification = json.loads(
            #     json_str, object_pairs_hook=keep_all_pairs
            # )
            print(f"  -> Parsed classification: {parsed_classification}")
            return parsed_classification, max_benefit, rent
        else:
            print("No JSON found in response.")
    except Exception as e:
        print(f"Error classifying {claim_file}: {str(e)}. ")
