# Standard categories for all security deposit items
STANDARD_CATEGORIES = {
    "CLEANING": "Cleaning services (carpet, house, deep clean, etc.)",
    "CARPET": "Carpet damage/replacement",
    "CARPET_CAUSED_BY_PET": "Carpet damage/replacement caused by pet",
    "PAINTING": "Paint and wall repairs",
    "LANDSCAPING": "Yard/garden/outdoor maintenance or plant replacement",
    "UTILITIES": "Unpaid utilities (electric, gas, water, etc.)",
    "RENT": "Unpaid rent",
    "LEASE_BREAK": "Lease break or early termination fees",
    "KEYS": "Key replacement or rekey services",
    "NORMAL_WEAR_AND_TEAR": "Normal wear and tear",
    "BEYOND_NORMAL_WEAR_AND_TEAR": "Beyond normal wear and tear",
    "PET": "Pet-related damage",
    "PEST": "Pest control services",
    "TRASH": "Trash removal or disposal",
    "ADMIN": "Administrative fees or taxes",
    "CREDIT": "Credits or refunds applied to tenant account",
    "OTHER": "Items that don't fit other categories",
}


FULLY_COVERED_CATEGORIES = {
    "CLEANING",
    "CARPET",
    "PAINTING",
    "UTILITIES",
    "KEYS",
    "BEYOND_NORMAL_WEAR_AND_TEAR",
    "PEST",
    "TRASH",
    "OTHER",
}
PARTIALLY_COVERED_CATEGORIES = {
    "LANDSCAPING",
    "CARPET_CAUSED_BY_PET",
    "RENT",
    "LEASE_BREAK",
}
NOT_COVERED_CATEGORIES = {"NORMAL_WEAR_AND_TEAR", "PET", "ADMIN"}
CREDIT_CATEGORIES = {"CREDIT"}
