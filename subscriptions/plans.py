from enum import Enum


class Plan(str, Enum):
    FREE = "free"
    TRIAL_7_DAY = "trial_7_day"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"
    PAST_DUE = "past_due"


# Data-driven plan catalog. Add a plan or tweak its features/duration/price
# here — entitlement and payment logic reads this rather than branching on
# plan names, and the server (never the client) is the source of truth for
# price. TODO: amount_minor_units below are placeholders — set real pricing
# before accepting live payments.
PLAN_CATALOG: dict[Plan, dict] = {
    Plan.FREE: {
        "label": "Free",
        "duration_days": None,
        "amount_minor_units": 0,
        "currency": "INR",
        "features": {"max_sessions_per_day": 1, "priority_support": False},
    },
    Plan.TRIAL_7_DAY: {
        "label": "7-Day Trial",
        "duration_days": 7,
        "amount_minor_units": 9900,
        "currency": "INR",
        "features": {"max_sessions_per_day": 10, "priority_support": False},
    },
    Plan.MONTHLY: {
        "label": "Monthly",
        "duration_days": 30,
        "amount_minor_units": 99900,
        "currency": "INR",
        "features": {"max_sessions_per_day": -1, "priority_support": True},
    },
    Plan.YEARLY: {
        "label": "Yearly",
        "duration_days": 365,
        "amount_minor_units": 999900,
        "currency": "INR",
        "features": {"max_sessions_per_day": -1, "priority_support": True},
    },
}
