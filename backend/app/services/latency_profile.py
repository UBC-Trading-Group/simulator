from typing import List


def normalize_latency_curve(latency_profile: str) -> List[float]:
    """
    Convert comma-separated weights to a normalized curve. Clients control
    the raw values, so malformed data will bubble up naturally.
    """
    weights = [
        float(part.strip()) for part in latency_profile.split(",") if part.strip()
    ]
    if not weights:
        return []

    total = sum(weights)
    return [weight / total for weight in weights]
