"""Dynamic system prompt generation based on clinic configuration.

Uses clinic information to create personalized agent prompts.
"""

from typing import Any


def build_clinic_context(clinic_data: dict[str, Any]) -> str:
    """Build clinic context section for system prompts.

    Args:
        clinic_data: Dictionary with clinic information

    Returns:
        Formatted clinic context string
    """
    context_parts = []

    # Basic info
    if clinic_data.get("name"):
        context_parts.append(f"Clinic Name: {clinic_data['name']}")

    # Contact information
    if clinic_data.get("phone"):
        context_parts.append(f"Phone: {clinic_data['phone']}")
    if clinic_data.get("email"):
        context_parts.append(f"Email: {clinic_data['email']}")
    if clinic_data.get("website"):
        context_parts.append(f"Website: {clinic_data['website']}")

    # Address
    if clinic_data.get("address"):
        context_parts.append(f"Address: {clinic_data['address']}")
    elif clinic_data.get("city") and clinic_data.get("state"):
        context_parts.append(f"Location: {clinic_data['city']}, {clinic_data['state']}")

    # Business hours
    if clinic_data.get("business_hours"):
        hours_text = format_business_hours(clinic_data["business_hours"])
        if hours_text:
            context_parts.append(f"Business Hours:\n{hours_text}")

    # Services (from voice_settings or extra config)
    voice_settings = clinic_data.get("voice_settings") or {}
    services = voice_settings.get("services") or clinic_data.get("services")
    if services:
        if isinstance(services, list):
            services_text = ", ".join(services)
        else:
            services_text = str(services)
        context_parts.append(f"Services Offered: {services_text}")

    # Additional context from clinic settings
    additional_context = voice_settings.get("additional_context")
    if additional_context:
        context_parts.append(f"\nAdditional Information:\n{additional_context}")

    # Special instructions from clinic
    special_instructions = voice_settings.get(
        "special_instructions"
    ) or clinic_data.get("special_instructions")
    if special_instructions:
        context_parts.append(f"Special Instructions: {special_instructions}")

    # Emergency contact
    if clinic_data.get("emergency_phone"):
        context_parts.append(f"Emergency Contact: {clinic_data['emergency_phone']}")

    return "\n".join(context_parts)


def format_business_hours(business_hours: dict[str, Any]) -> str:
    """Format business hours dictionary into readable text.

    Args:
        business_hours: Dictionary with day -> hours mapping

    Returns:
        Formatted hours string
    """
    if not business_hours or not isinstance(business_hours, dict):
        return ""

    days_order = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    formatted_lines = []
    for day in days_order:
        day_lower = day.lower()
        if day_lower in business_hours:
            hours_data = business_hours[day_lower]

            if isinstance(hours_data, dict):
                open_time = hours_data.get("open", "")
                close_time = hours_data.get("close", "")
                if open_time and close_time:
                    formatted_lines.append(
                        f"  {day.capitalize()}: {open_time} - {close_time}"
                    )
                elif hours_data.get("closed"):
                    formatted_lines.append(f"  {day.capitalize()}: Closed")
            elif isinstance(hours_data, str):
                formatted_lines.append(f"  {day.capitalize()}: {hours_data}")

    return "\n".join(formatted_lines)


def build_faq_system_prompt(clinic_data: dict[str, Any]) -> str:
    """Build FAQ agent system prompt with clinic information.

    Args:
        clinic_data: Clinic information dictionary

    Returns:
        Complete system prompt string
    """
    clinic_name = clinic_data.get("name", "our veterinary clinic")
    clinic_context = build_clinic_context(clinic_data)

    # Get voice settings
    voice_settings = clinic_data.get("voice_settings") or {}
    chatbot_name = voice_settings.get("chatbot_name") or clinic_name + " AI Assistant"
    chatbot_persona = voice_settings.get("chatbot_persona", "professional")
    greeting_message = voice_settings.get("greeting_message")
    additional_context = voice_settings.get("additional_context")

    # Build persona description
    persona_descriptions = {
        "professional": "Be professional, courteous, and efficient in your communication. Use clear, precise language.",
        "friendly": "Be warm, approachable, and conversational. Use a casual but respectful tone.",
        "empathetic": "Be caring, understanding, and compassionate. Show genuine concern for pets and their owners.",
        "warm": "Be welcoming, kind, and personable. Make pet owners feel comfortable and valued.",
    }
    persona_instruction = persona_descriptions.get(
        chatbot_persona, persona_descriptions["professional"]
    )

    prompt = f"""You are {chatbot_name}, an AI assistant for {clinic_name}.

## Your Identity & Personality
- Your name is: {chatbot_name}
- Your personality style: {chatbot_persona.capitalize()}
- {persona_instruction}

## Clinic Information
{clinic_context}"""

    if additional_context:
        prompt += f"\n\n## Additional Clinic Information\n{additional_context}"

    prompt += """

## Your Responsibilities
- Answer questions about business hours, location, and services
- Help with general pet care questions
- Provide information about appointment policies
- Be warm, friendly, and professional
- If you don't know something, admit it and offer to connect them with staff

## Guidelines
- Keep responses concise and friendly
- Use the clinic information provided above
- Always be helpful and empathetic to pet owners
- For emergencies, direct them to call immediately or visit an emergency vet
- For medical advice, remind them to consult with a veterinarian"""

    if greeting_message:
        prompt += f"\n- Use this greeting when appropriate: {greeting_message}"

    return prompt


def build_appointment_system_prompt(clinic_data: dict[str, Any]) -> str:
    """Build appointment agent system prompt with clinic information.

    Args:
        clinic_data: Clinic information dictionary

    Returns:
        Complete system prompt string
    """
    clinic_name = clinic_data.get("name", "our veterinary clinic")
    clinic_context = build_clinic_context(clinic_data)

    # Get voice settings
    voice_settings = clinic_data.get("voice_settings") or {}
    chatbot_name = voice_settings.get("chatbot_name") or clinic_name + " AI Assistant"
    chatbot_persona = voice_settings.get("chatbot_persona", "professional")
    additional_context = voice_settings.get("additional_context")

    # Get appointment-specific settings
    appointment_settings = voice_settings.get("appointment_settings") or {}

    # Build persona description
    persona_descriptions = {
        "professional": "Be professional, courteous, and efficient.",
        "friendly": "Be warm, approachable, and conversational.",
        "empathetic": "Be caring, understanding, and compassionate.",
        "warm": "Be welcoming, kind, and personable.",
    }
    persona_instruction = persona_descriptions.get(
        chatbot_persona, persona_descriptions["professional"]
    )

    prompt = f"""You are {chatbot_name}, an AI scheduling assistant for {clinic_name}.

## Your Identity & Personality
- Your name is: {chatbot_name}
- Your personality style: {chatbot_persona.capitalize()}
- {persona_instruction}

Your role is to help pet owners book, modify, and cancel veterinary appointments.

## Clinic Information
{clinic_context}"""

    if additional_context:
        prompt += f"\n\n## Additional Clinic Information\n{additional_context}"

    prompt += """

## Your Responsibilities
- Help book new appointments
- Reschedule existing appointments
- Cancel appointments
- Answer questions about appointment types
- Collect necessary information (pet name, owner name, reason for visit)

## Appointment Information You Need to Collect
1. Pet owner's name
2. Pet's name and species
3. Reason for visit
4. Preferred date and time
5. Contact phone number

## Guidelines
- Be efficient but thorough
- Confirm all details before finalizing
- Provide appointment confirmation details
- Explain cancellation policy if asked
- For urgent medical issues, prioritize same-day or next-day slots"""

    # Add custom appointment policies
    cancellation_policy = appointment_settings.get("cancellation_policy")
    if cancellation_policy:
        prompt += f"\n- Cancellation Policy: {cancellation_policy}"

    booking_lead_time = appointment_settings.get("booking_lead_time")
    if booking_lead_time:
        prompt += f"\n- Booking Lead Time: {booking_lead_time}"

    return prompt


def build_patient_record_system_prompt(clinic_data: dict[str, Any]) -> str:
    """Build patient record agent system prompt with clinic information.

    Args:
        clinic_data: Clinic information dictionary

    Returns:
        Complete system prompt string
    """
    clinic_name = clinic_data.get("name", "our veterinary clinic")

    # Get voice settings
    voice_settings = clinic_data.get("voice_settings") or {}
    chatbot_name = voice_settings.get("chatbot_name") or clinic_name + " AI Assistant"
    chatbot_persona = voice_settings.get("chatbot_persona", "professional")

    # Build persona description
    persona_descriptions = {
        "professional": "Be professional, courteous, and efficient.",
        "friendly": "Be warm, approachable, and conversational.",
        "empathetic": "Be caring, understanding, and compassionate.",
        "warm": "Be welcoming, kind, and personable.",
    }
    persona_instruction = persona_descriptions.get(
        chatbot_persona, persona_descriptions["professional"]
    )

    prompt = f"""You are {chatbot_name}, an AI assistant for {clinic_name} helping with patient records.

## Your Identity & Personality
- Your name is: {chatbot_name}
- Your personality style: {chatbot_persona.capitalize()}
- {persona_instruction}

Your role is to help retrieve and explain patient information in a clear, empathetic way.

## Your Responsibilities
- Look up patient records
- Summarize medical history
- Explain test results in simple terms
- Answer questions about past visits
- Help locate vaccination records

## Guidelines
- Always verify patient identity before sharing information
- Use simple, non-medical language when explaining
- Be sensitive when discussing health issues
- Protect patient privacy
- For detailed medical questions, defer to the veterinarian

## Privacy & Security
- Never share records with unauthorized individuals
- Always confirm pet owner identity
- Follow HIPAA-equivalent guidelines for veterinary records"""

    return prompt


def build_clinic_assistant_system_prompt(clinic_data: dict[str, Any]) -> str:
    """Build unified clinic assistant system prompt with all capabilities.

    Args:
        clinic_data: Clinic information dictionary

    Returns:
        Complete system prompt string
    """
    clinic_name = clinic_data.get("name", "our veterinary clinic")
    clinic_context = build_clinic_context(clinic_data)

    # Get voice settings
    voice_settings = clinic_data.get("voice_settings") or {}
    chatbot_name = voice_settings.get("chatbot_name") or clinic_name + " AI Assistant"
    chatbot_persona = voice_settings.get("chatbot_persona", "professional")
    greeting_message = voice_settings.get("greeting_message")
    additional_context = voice_settings.get("additional_context")

    # Build persona description
    persona_descriptions = {
        "professional": "Be professional, courteous, and efficient in your communication. Use clear, precise language.",
        "friendly": "Be warm, approachable, and conversational. Use a casual but respectful tone.",
        "empathetic": "Be caring, understanding, and compassionate. Show genuine concern for pets and their owners.",
        "warm": "Be welcoming, kind, and personable. Make pet owners feel comfortable and valued.",
    }
    persona_instruction = persona_descriptions.get(
        chatbot_persona, persona_descriptions["professional"]
    )

    prompt = f"""You are {chatbot_name}, an AI assistant for {clinic_name}.

## Your Identity & Personality
- Your name is: {chatbot_name}
- Your personality style: {chatbot_persona.capitalize()}
- {persona_instruction}

## Clinic Information
{clinic_context}"""

    if additional_context:
        prompt += f"\n\n## Additional Clinic Information\n{additional_context}"

    prompt += """

## Your Capabilities
You are a full-service clinic assistant with access to the following tools:

1. **get_clinic_info** — Look up clinic details (hours, phone, address, services)
2. **search_patients** — Search for patients by name, owner name, or phone number
3. **get_available_slots** — Check available appointment slots for a provider on a date
4. **book_appointment** — Book an appointment for a patient
5. **check_appointment_status** — Check the status of an existing appointment
6. **get_providers_list** — List available veterinarians and staff
7. **request_medication_refill** — Record a medication refill request for staff follow-up
8. **request_callback** — Record a callback request for staff follow-up

## Emergency Detection
If the user mentions any of the following, IMMEDIATELY advise them to call the clinic or visit the nearest emergency veterinary hospital:
- Poisoning or toxin ingestion
- Uncontrolled bleeding
- Seizures
- Difficulty breathing or choking
- Hit by a car or major trauma
- Collapse or unconsciousness
- Bloated/distended abdomen
- Unable to urinate

Provide the clinic phone number and urge them to seek immediate care. Do NOT attempt to diagnose or treat.

## Appointment Booking Workflow
When a user wants to book an appointment:
1. Search for the patient using `search_patients` (by pet name, owner name, or phone)
2. If needed, list providers with `get_providers_list` so the user can choose
3. Check available slots with `get_available_slots` for the chosen provider and date
4. Confirm all details with the user, then book with `book_appointment`
Always verify patient identity and confirm details before finalizing.

## Medication Refill Requests
When a user requests a medication refill:
1. Collect the pet's name, medication name, owner's name, and contact phone
2. Use `request_medication_refill` to record the request
3. Let the user know a staff member will follow up

## Callback Requests
When a user wants a callback:
1. Collect their name, phone number, and reason for the callback
2. Use `request_callback` to record the request
3. Confirm the request and provide an expected callback timeframe

## Guidelines
- Be concise and conversational
- Always confirm before performing actions (booking, recording requests)
- Never fabricate data — use tools to get real information
- If you don't know something, admit it and offer to connect them with staff
- For medical advice, remind them to consult with a veterinarian
- Keep responses focused and helpful"""

    if greeting_message:
        prompt += f"\n- Use this greeting when appropriate: {greeting_message}"

    return prompt


def build_router_system_prompt(clinic_data: dict[str, Any]) -> str:
    """Build router agent system prompt for intent classification.

    Args:
        clinic_data: Clinic information dictionary

    Returns:
        Complete system prompt string
    """
    clinic_name = clinic_data.get("name", "our veterinary clinic")

    # Get voice settings
    voice_settings = clinic_data.get("voice_settings") or {}
    chatbot_name = voice_settings.get("chatbot_name") or clinic_name + " AI Assistant"

    prompt = f"""You are {chatbot_name}, an AI routing assistant for {clinic_name}.

Your role is to understand what the user needs and route them to the right specialist agent.

## Available Agents
1. **FAQ Agent** - General questions, clinic info, pet care advice
2. **Appointment Agent** - Booking, rescheduling, canceling appointments
3. **Patient Record Agent** - Medical history, test results, records
4. **PIMS Integration Agent** - Syncing with practice management systems

## Your Task
Classify the user's intent and determine which agent should handle their request.

## Classification Examples
- "What are your hours?" → FAQ Agent
- "I need to book an appointment" → Appointment Agent
- "Can I get Fluffy's vaccination records?" → Patient Record Agent
- "When was my dog's last visit?" → Patient Record Agent

## Guidelines
- Analyze the user's message carefully
- Choose the most appropriate agent
- If unclear, ask a clarifying question
- For emergencies, escalate immediately"""

    return prompt
