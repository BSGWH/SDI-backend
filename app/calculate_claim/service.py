from app.classify_items.utils import (
    STANDARD_CATEGORIES,
    FULLY_COVERED_CATEGORIES,
    PARTIALLY_COVERED_CATEGORIES,
    NOT_COVERED_CATEGORIES,
)


def calculate_claim(
    parsed_classification: dict, max_benefit: float, rent: float, amount_of_claim: float
):
    calculation_process = ""
    covered_items = "Covered items: "
    partially_covered_items = "Partially covered items: "
    not_covered_items = "Not covered items: "

    total_claim = 0.0
    if not parsed_classification:
        return {"status": "Declined", "reason": "No items classified"}
    for item, amount_category_reasoning in parsed_classification.items():
        if amount_category_reasoning["category"] not in STANDARD_CATEGORIES.keys():
            continue
        amount = amount_category_reasoning["amount"]
        if not amount:
            continue
        category = amount_category_reasoning["category"]
        if category in FULLY_COVERED_CATEGORIES:
            calculation_process += f"+{amount} ({item}fully covered) "
            covered_items += f"{item}, "
            total_claim += amount
        elif category in PARTIALLY_COVERED_CATEGORIES:
            if category == "LANDSCAPING":
                if amount > 500:
                    amount = 500
            elif category == "CARPET_CAUSED_BY_PET":
                amount = amount * 0.6
            elif category == "RENT":
                if amount > rent:
                    amount = rent
            elif category == "LEASE_BREAK":
                if amount > rent:
                    amount = rent
            calculation_process += f"+{amount} ({item}partial covered) "
            partially_covered_items += f"{item}, "
            total_claim += amount
        elif category in NOT_COVERED_CATEGORIES:
            not_covered_items += f"{item}, "
        elif category == "CREDIT":
            calculation_process += f"-{amount} ({item}credit) "
            total_claim -= amount
    if total_claim > max_benefit:
        total_claim = max_benefit
        calculation_process += f" (capped at max benefit {max_benefit})"
    if total_claim > amount_of_claim:
        total_claim = amount_of_claim
        calculation_process += f" (capped at claim amount {amount_of_claim})"

    parsed_classification["calculation_process"] = calculation_process.strip()
    parsed_classification["covered_items"] = covered_items.strip(", ")
    parsed_classification["partially_covered_items"] = partially_covered_items.strip(
        ","
    )
    parsed_classification["not_covered_items"] = not_covered_items.strip(", ")
    parsed_classification["total_claim"] = total_claim
    return parsed_classification


if __name__ == "__main__":
    parsed_classification = {
        "Overgrown lawn and shrubs": {
            "amount": 150.0,
            "category": "LANDSCAPING",
            "reasoning": "Tenant responsible for maintaining yard condition",
        },
        "Missing left side upstairs and right side exterior dryer": {
            "amount": None,
            "category": "BEYOND_NORMAL_WEAR_AND_TEAR",
            "reasoning": "Missing appliance components beyond normal usage",
        },
        "Damaged right front lower window screen": {
            "amount": None,
            "category": "BEYOND_NORMAL_WEAR_AND_TEAR",
            "reasoning": "Window screen damage exceeds normal wear",
        },
        "Home rekeyed due to eviction": {
            "amount": None,
            "category": "KEYS",
            "reasoning": "Rekey service required due to tenant move-out",
        },
        "Drywall damage": {
            "amount": None,
            "category": "BEYOND_NORMAL_WEAR_AND_TEAR",
            "reasoning": "Multiple room drywall damage beyond normal wear",
        },
        "Peel and stick laminate on kitchen countertops": {
            "amount": None,
            "category": "BEYOND_NORMAL_WEAR_AND_TEAR",
            "reasoning": "Unauthorized modification of property surfaces",
        },
        "Stains and dirt/ markings in kitchen cabinets and drawers": {
            "amount": None,
            "category": "CLEANING",
            "reasoning": "Excessive dirt and staining requiring professional cleaning",
        },
        "Damaged blinds": {
            "amount": None,
            "category": "BEYOND_NORMAL_WEAR_AND_TEAR",
            "reasoning": "Multiple blind damages exceeding normal usage",
        },
        "Missing shower head and toilet seat in main floor bathroom": {
            "amount": None,
            "category": "BEYOND_NORMAL_WEAR_AND_TEAR",
            "reasoning": "Missing bathroom fixtures",
        },
        "Damaged front entrance door": {
            "amount": 400.0,
            "category": "BEYOND_NORMAL_WEAR_AND_TEAR",
            "reasoning": "Significant entrance door damage",
        },
        "Permanent carpet stains": {
            "amount": None,
            "category": "CARPET",
            "reasoning": "Permanent staining requiring carpet replacement",
        },
        "Damaged laminate on kitchen master bathroom cabinet doors": {
            "amount": None,
            "category": "BEYOND_NORMAL_WEAR_AND_TEAR",
            "reasoning": "Unauthorized modifications and damage to cabinet surfaces",
        },
        "Damaged door in right rear upstairs bedroom": {
            "amount": None,
            "category": "BEYOND_NORMAL_WEAR_AND_TEAR",
            "reasoning": "Door damage beyond normal wear",
        },
        "Two attic air filters not changed": {
            "amount": 70.0,
            "category": "BEYOND_NORMAL_WEAR_AND_TEAR",
            "reasoning": "Failure to maintain HVAC system components",
        },
        "No carpet cleaning receipt": {
            "amount": 500.0,
            "category": "CLEANING",
            "reasoning": "Required carpet cleaning not performed by tenant",
        },
        "Excessive dirt, grime, trash left behind": {
            "amount": 500.0,
            "category": "CLEANING",
            "reasoning": "Extensive cleaning required due to tenant's poor maintenance",
        },
        "Missing garage remote": {
            "amount": 80.0,
            "category": "BEYOND_NORMAL_WEAR_AND_TEAR",
            "reasoning": "Missing property accessory",
        },
    }
    max_benefit = 4000
    rent = 2205
    amount_of_claim = 4000
    result = calculate_claim(parsed_classification, max_benefit, rent, amount_of_claim)
    print(f"  -> Calculated claim: {result}")
