from app.classify_items.utils import (
    STANDARD_CATEGORIES,
    FULLY_COVERED_CATEGORIES,
    PARTIALLY_COVERED_CATEGORIES,
    NOT_COVERED_CATEGORIES,
)


def calculate_claim(parsed_classification: dict, max_benefit: float, rent: float):
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
    if total_claim > max_benefit:
        total_claim = max_benefit
        calculation_process += f" (capped at max benefit {max_benefit})"

    parsed_classification["calculation_process"] = calculation_process.strip()
    parsed_classification["covered_items"] = covered_items.strip(", ")
    parsed_classification["partially_covered_items"] = partially_covered_items.strip(
        ","
    )
    parsed_classification["not_covered_items"] = not_covered_items.strip(", ")
    parsed_classification["total_claim"] = total_claim
    return parsed_classification
