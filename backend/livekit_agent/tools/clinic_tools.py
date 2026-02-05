"""
Clinic Information Tools

Tools for providing clinic information to callers.
These use cached data loaded at session start for low latency.
"""

import logging

logger = logging.getLogger(__name__)


def format_business_hours(hours_dict: dict | None) -> str:
    """
    Format business hours dictionary into a readable string.

    Args:
        hours_dict: Dictionary with day names as keys and hours as values

    Returns:
        Human-readable string for voice response
    """
    if not hours_dict:
        return "I don't have the business hours on file. Please hold while I transfer you to someone who can help."

    days_order = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    formatted_parts = []
    for day in days_order:
        hours = hours_dict.get(day)
        if hours:
            if hours.lower() in ["closed", "none", ""]:
                formatted_parts.append(f"{day.capitalize()}: Closed")
            else:
                formatted_parts.append(f"{day.capitalize()}: {hours}")

    return ". ".join(formatted_parts)


def get_clinic_hours(cached_hours: dict | None) -> str:
    """
    Get clinic business hours.

    Uses pre-cached data for instant response.

    Args:
        cached_hours: Pre-loaded business hours from session start

    Returns:
        Voice-friendly string with clinic hours
    """
    hours_str = format_business_hours(cached_hours)
    return f"Our hours are: {hours_str}"


def get_clinic_location(cached_clinic: dict) -> str:
    """
    Get clinic address and location info.

    Args:
        cached_clinic: Pre-loaded clinic data

    Returns:
        Voice-friendly string with clinic location
    """
    address = cached_clinic.get("address")
    city = cached_clinic.get("city")
    state = cached_clinic.get("state")
    zip_code = cached_clinic.get("zip_code")

    if not address:
        return "I don't have the address on file. Would you like me to transfer you to someone who can provide directions?"

    location_parts = [address]
    if city:
        location_parts.append(city)
    if state:
        location_parts.append(state)
    if zip_code:
        location_parts.append(zip_code)

    return f"We're located at {', '.join(location_parts)}."


def get_clinic_services(cached_clinic: dict) -> str:
    """
    Get list of services offered by the clinic.

    Args:
        cached_clinic: Pre-loaded clinic data

    Returns:
        Voice-friendly string with services
    """
    services = cached_clinic.get("services", [])

    if not services:
        return "We offer a full range of veterinary services including wellness exams, vaccinations, surgery, dental care, and emergency services. Would you like me to connect you with our staff for specific questions about a service?"

    if len(services) <= 3:
        return f"We offer {', '.join(services)}. Is there a specific service you're interested in?"

    # For many services, just list a few
    top_services = services[:4]
    return f"We offer {', '.join(top_services)}, and more. What service are you interested in?"
