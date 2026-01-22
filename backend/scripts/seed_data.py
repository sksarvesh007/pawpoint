#!/usr/bin/env python
# ruff: noqa: T201, S311
"""
Seed Data Script for PawPoint Development

Creates sample data for local development and testing.
T201 (print) and S311 (random) are expected for this CLI script.

Prerequisites:
    - PostgreSQL database running (docker compose up db)
    - DATABASE_URL configured in dev.env

Usage:
    cd backend
    PYTHONPATH=. uv run python scripts/seed_data.py           # Seed database
    PYTHONPATH=. uv run python scripts/seed_data.py --clear   # Clear and re-seed
    PYTHONPATH=. uv run python scripts/seed_data.py --minimal # Minimal data set

Options:
    --clear     Clear existing data before seeding
    --minimal   Create minimal seed data (1 clinic, few records)

Creates:
    - 5 users (super_admin, admin, staff, viewer roles)
    - 2 clinics (Happy Paws in SF, City Pet in NYC)
    - 5 providers (veterinarians, technicians)
    - 40 patients (dogs, cats, birds)
    - ~80 appointments (past, today, future)
    - ~10 call logs (for voice-enabled clinic)
"""

import argparse
import asyncio
import random
import sys
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select, text

from app.db import async_session_factory, engine
from app.models import Appointment, CallLog, Clinic, Patient, Provider, User
from app.models.appointment import AppointmentSource, AppointmentStatus, AppointmentType
from app.models.call_log import CallDirection, CallOutcome, CallStatus
from app.models.clinic import PIMSConnectionStatus, PIMSType
from app.models.patient import Sex, Species
from app.models.provider import ProviderType
from app.models.user import UserRole, user_clinic_association

# Sample data constants
DOG_BREEDS = [
    "Golden Retriever",
    "Labrador Retriever",
    "German Shepherd",
    "Bulldog",
    "Poodle",
    "Beagle",
    "Rottweiler",
    "Yorkshire Terrier",
    "Boxer",
    "Dachshund",
    "Husky",
    "Corgi",
    "Shih Tzu",
    "Chihuahua",
    "Mixed Breed",
]

CAT_BREEDS = [
    "Persian",
    "Maine Coon",
    "Siamese",
    "British Shorthair",
    "Ragdoll",
    "Bengal",
    "Abyssinian",
    "Sphynx",
    "Scottish Fold",
    "Domestic Shorthair",
]

PET_NAMES = [
    "Max",
    "Bella",
    "Charlie",
    "Luna",
    "Cooper",
    "Daisy",
    "Buddy",
    "Lucy",
    "Rocky",
    "Sadie",
    "Duke",
    "Molly",
    "Bear",
    "Bailey",
    "Tucker",
    "Maggie",
    "Jack",
    "Sophie",
    "Oliver",
    "Chloe",
    "Leo",
    "Penny",
    "Milo",
    "Zoey",
    "Winston",
    "Lily",
    "Teddy",
    "Stella",
    "Murphy",
    "Nala",
]

FIRST_NAMES = [
    "James",
    "Mary",
    "John",
    "Patricia",
    "Robert",
    "Jennifer",
    "Michael",
    "Linda",
    "William",
    "Elizabeth",
    "David",
    "Barbara",
    "Richard",
    "Susan",
    "Joseph",
    "Jessica",
    "Thomas",
    "Sarah",
    "Christopher",
    "Karen",
]

LAST_NAMES = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Hernandez",
    "Lopez",
    "Gonzalez",
    "Wilson",
    "Anderson",
    "Thomas",
    "Taylor",
    "Moore",
    "Jackson",
    "Martin",
]

PET_COLORS = [
    "Black",
    "White",
    "Brown",
    "Golden",
    "Gray",
    "Orange",
    "Cream",
    "Brindle",
    "Spotted",
    "Tan",
]

VISIT_REASONS = [
    "Annual wellness exam",
    "Vaccination update",
    "Not eating well",
    "Limping on left leg",
    "Skin irritation",
    "Vomiting for 2 days",
    "Ear infection symptoms",
    "Dental check",
    "Weight management consultation",
    "Post-surgery follow-up",
    "Lethargy and decreased activity",
    "Eye discharge",
    "Coughing",
    "Diarrhea",
    "Itching and scratching",
]


def random_phone() -> str:
    """Generate a random US phone number in E.164 format."""
    area_code = random.randint(200, 999)
    prefix = random.randint(200, 999)
    line = random.randint(1000, 9999)
    return f"+1{area_code}{prefix}{line}"


def random_date_of_birth(min_years: int = 0, max_years: int = 15) -> date:
    """Generate a random date of birth for a pet."""
    days_ago = random.randint(min_years * 365, max_years * 365)
    return date.today() - timedelta(days=days_ago)


def random_datetime_range(start_days: int, end_days: int) -> datetime:
    """Generate a random datetime within a range of days from now."""
    base = datetime.now(UTC)
    offset_days = random.randint(start_days, end_days)
    offset_hours = random.randint(8, 17)  # Business hours
    offset_minutes = random.choice([0, 15, 30, 45])
    return base.replace(
        hour=offset_hours,
        minute=offset_minutes,
        second=0,
        microsecond=0,
    ) + timedelta(days=offset_days)


async def clear_data() -> None:
    """Clear all existing seed data from the database."""
    print("Clearing existing data...")
    async with async_session_factory() as session:
        # Delete in order respecting foreign keys
        await session.execute(text("DELETE FROM appointments"))
        await session.execute(text("DELETE FROM call_logs"))
        await session.execute(text("DELETE FROM patients"))
        await session.execute(text("DELETE FROM providers"))
        await session.execute(text("DELETE FROM user_clinic_associations"))
        await session.execute(text("DELETE FROM clinics"))
        await session.execute(text("DELETE FROM users"))
        await session.execute(text("DELETE FROM pims_sync_logs"))
        await session.commit()
    print("Data cleared.")


async def create_users() -> list[User]:
    """Create sample users."""
    print("Creating users...")

    users_data = [
        {
            "email": "admin@pawpoint.dev",
            "first_name": "Admin",
            "last_name": "User",
            "role": UserRole.SUPER_ADMIN,
            "email_verified": True,
            "password_hash": "hashed_password_placeholder",  # Not used for dev
        },
        {
            "email": "dr.sarah@happypaws.dev",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "role": UserRole.ADMIN,
            "email_verified": True,
            "password_hash": "hashed_password_placeholder",
        },
        {
            "email": "mike@happypaws.dev",
            "first_name": "Mike",
            "last_name": "Chen",
            "role": UserRole.STAFF,
            "email_verified": True,
            "password_hash": "hashed_password_placeholder",
        },
        {
            "email": "emily@citypet.dev",
            "first_name": "Emily",
            "last_name": "Williams",
            "role": UserRole.ADMIN,
            "email_verified": True,
            "password_hash": "hashed_password_placeholder",
        },
        {
            "email": "viewer@pawpoint.dev",
            "first_name": "View",
            "last_name": "Only",
            "role": UserRole.VIEWER,
            "email_verified": True,
            "password_hash": "hashed_password_placeholder",
        },
    ]

    users = []
    async with async_session_factory() as session:
        for data in users_data:
            user = User(**data)
            session.add(user)
            users.append(user)
        await session.commit()

        # Refresh to get IDs
        for user in users:
            await session.refresh(user)

    print(f"  Created {len(users)} users")
    return users


async def create_clinics() -> list[Clinic]:
    """Create sample clinics."""
    print("Creating clinics...")

    clinics_data = [
        {
            "name": "Happy Paws Veterinary Clinic",
            "slug": "happy-paws",
            "description": "A full-service veterinary clinic providing compassionate care for your furry family members.",
            "phone": "+15551234567",
            "email": "info@happypaws.dev",
            "website": "https://happypaws.dev",
            "address_line1": "123 Main Street",
            "city": "San Francisco",
            "state": "CA",
            "postal_code": "94102",
            "country": "US",
            "timezone": "America/Los_Angeles",
            "is_active": True,
            "pims_type": PIMSType.EZYVET,
            "pims_connection_status": PIMSConnectionStatus.CONNECTED,
            "voice_enabled": True,
            "twilio_phone_number": "+15559876543",
            "emergency_phone": "+15559911111",
            "business_hours": {
                "monday": {"open": "08:00", "close": "18:00"},
                "tuesday": {"open": "08:00", "close": "18:00"},
                "wednesday": {"open": "08:00", "close": "18:00"},
                "thursday": {"open": "08:00", "close": "18:00"},
                "friday": {"open": "08:00", "close": "17:00"},
                "saturday": {"open": "09:00", "close": "14:00"},
                "sunday": {"closed": True},
            },
        },
        {
            "name": "City Pet Hospital",
            "slug": "city-pet",
            "description": "24/7 emergency and specialty veterinary care in the heart of downtown.",
            "phone": "+15552345678",
            "email": "contact@citypet.dev",
            "website": "https://citypet.dev",
            "address_line1": "456 Oak Avenue",
            "address_line2": "Suite 100",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "US",
            "timezone": "America/New_York",
            "is_active": True,
            "pims_type": PIMSType.VETSPIRE,
            "pims_connection_status": PIMSConnectionStatus.DISCONNECTED,
            "voice_enabled": False,
            "business_hours": {
                "monday": {"open": "00:00", "close": "23:59"},
                "tuesday": {"open": "00:00", "close": "23:59"},
                "wednesday": {"open": "00:00", "close": "23:59"},
                "thursday": {"open": "00:00", "close": "23:59"},
                "friday": {"open": "00:00", "close": "23:59"},
                "saturday": {"open": "00:00", "close": "23:59"},
                "sunday": {"open": "00:00", "close": "23:59"},
            },
        },
    ]

    clinics = []
    async with async_session_factory() as session:
        for data in clinics_data:
            clinic = Clinic(**data)
            session.add(clinic)
            clinics.append(clinic)
        await session.commit()

        for clinic in clinics:
            await session.refresh(clinic)

    print(f"  Created {len(clinics)} clinics")
    return clinics


async def associate_users_clinics(users: list[User], clinics: list[Clinic]) -> None:
    """Associate users with clinics."""
    print("Associating users with clinics...")

    async with async_session_factory() as session:
        # Super admin has access to all clinics (but we don't need explicit association)
        # Sarah (admin) -> Happy Paws
        # Mike (staff) -> Happy Paws
        # Emily (admin) -> City Pet
        # Viewer -> Both clinics

        associations = [
            (users[1].id, clinics[0].id),  # Sarah -> Happy Paws
            (users[2].id, clinics[0].id),  # Mike -> Happy Paws
            (users[3].id, clinics[1].id),  # Emily -> City Pet
            (users[4].id, clinics[0].id),  # Viewer -> Happy Paws
            (users[4].id, clinics[1].id),  # Viewer -> City Pet
        ]

        for user_id, clinic_id in associations:
            await session.execute(
                user_clinic_association.insert().values(
                    user_id=user_id, clinic_id=clinic_id
                )
            )
        await session.commit()

    print(f"  Created {len(associations)} user-clinic associations")


async def create_providers(clinics: list[Clinic]) -> list[Provider]:
    """Create sample providers for each clinic."""
    print("Creating providers...")

    providers = []
    async with async_session_factory() as session:
        # Happy Paws providers
        happy_paws_providers = [
            {
                "clinic_id": clinics[0].id,
                "first_name": "Sarah",
                "last_name": "Johnson",
                "title": "DVM",
                "email": "dr.sarah@happypaws.dev",
                "phone": "+15551112222",
                "provider_type": ProviderType.VETERINARIAN,
                "license_number": "CA-VET-12345",
                "specialties": ["general practice", "dentistry"],
                "bio": "Dr. Johnson has over 10 years of experience in small animal medicine.",
                "is_active": True,
                "accepts_appointments": True,
                "default_appointment_duration_min": 30,
                "color": "#4A90D9",
                "display_order": 1,
                "availability": {
                    "monday": [{"start": "08:00", "end": "17:00"}],
                    "tuesday": [{"start": "08:00", "end": "17:00"}],
                    "wednesday": [{"start": "08:00", "end": "17:00"}],
                    "thursday": [{"start": "08:00", "end": "17:00"}],
                    "friday": [{"start": "08:00", "end": "15:00"}],
                },
            },
            {
                "clinic_id": clinics[0].id,
                "first_name": "David",
                "last_name": "Park",
                "title": "DVM",
                "email": "dr.david@happypaws.dev",
                "phone": "+15551113333",
                "provider_type": ProviderType.VETERINARIAN,
                "license_number": "CA-VET-67890",
                "specialties": ["surgery", "orthopedics"],
                "bio": "Dr. Park specializes in orthopedic surgery and rehabilitation.",
                "is_active": True,
                "accepts_appointments": True,
                "default_appointment_duration_min": 45,
                "color": "#50C878",
                "display_order": 2,
                "availability": {
                    "monday": [{"start": "09:00", "end": "18:00"}],
                    "tuesday": [{"start": "09:00", "end": "18:00"}],
                    "wednesday": [{"start": "09:00", "end": "18:00"}],
                    "thursday": [{"start": "09:00", "end": "18:00"}],
                },
            },
            {
                "clinic_id": clinics[0].id,
                "first_name": "Lisa",
                "last_name": "Martinez",
                "title": "RVT",
                "email": "lisa@happypaws.dev",
                "phone": "+15551114444",
                "provider_type": ProviderType.VET_TECHNICIAN,
                "license_number": "CA-RVT-11111",
                "specialties": ["lab work", "vaccinations"],
                "is_active": True,
                "accepts_appointments": True,
                "default_appointment_duration_min": 15,
                "color": "#FFB347",
                "display_order": 3,
            },
        ]

        # City Pet providers
        city_pet_providers = [
            {
                "clinic_id": clinics[1].id,
                "first_name": "Emily",
                "last_name": "Williams",
                "title": "DVM, DACVIM",
                "email": "dr.emily@citypet.dev",
                "phone": "+15552221111",
                "provider_type": ProviderType.SPECIALIST,
                "license_number": "NY-VET-54321",
                "specialties": ["internal medicine", "oncology"],
                "bio": "Dr. Williams is board-certified in veterinary internal medicine.",
                "is_active": True,
                "accepts_appointments": True,
                "default_appointment_duration_min": 60,
                "color": "#9B59B6",
                "display_order": 1,
            },
            {
                "clinic_id": clinics[1].id,
                "first_name": "James",
                "last_name": "Thompson",
                "title": "DVM",
                "email": "dr.james@citypet.dev",
                "phone": "+15552222222",
                "provider_type": ProviderType.VETERINARIAN,
                "license_number": "NY-VET-98765",
                "specialties": ["emergency medicine", "critical care"],
                "bio": "Dr. Thompson leads our 24/7 emergency team.",
                "is_active": True,
                "accepts_appointments": True,
                "default_appointment_duration_min": 30,
                "color": "#E74C3C",
                "display_order": 2,
            },
        ]

        all_providers = happy_paws_providers + city_pet_providers
        for data in all_providers:
            provider = Provider(**data)
            session.add(provider)
            providers.append(provider)

        await session.commit()

        for provider in providers:
            await session.refresh(provider)

    print(f"  Created {len(providers)} providers")
    return providers


async def create_patients(
    clinics: list[Clinic], count_per_clinic: int = 20
) -> list[Patient]:
    """Create sample patients for each clinic."""
    print("Creating patients...")

    patients = []
    async with async_session_factory() as session:
        for clinic in clinics:
            for _ in range(count_per_clinic):
                species = random.choice(
                    [Species.DOG, Species.DOG, Species.CAT, Species.CAT, Species.BIRD]
                )
                breed = None
                if species == Species.DOG:
                    breed = random.choice(DOG_BREEDS)
                elif species == Species.CAT:
                    breed = random.choice(CAT_BREEDS)
                elif species == Species.BIRD:
                    breed = random.choice(["Parakeet", "Cockatiel", "Parrot", "Canary"])

                sex = random.choice(list(Sex))
                owner_first = random.choice(FIRST_NAMES)
                owner_last = random.choice(LAST_NAMES)

                patient = Patient(
                    clinic_id=clinic.id,
                    name=random.choice(PET_NAMES),
                    species=species,
                    breed=breed,
                    color=random.choice(PET_COLORS),
                    sex=sex,
                    date_of_birth=random_date_of_birth(),
                    weight_kg=round(random.uniform(2.0, 40.0), 1)
                    if species == Species.DOG
                    else round(random.uniform(2.0, 8.0), 1),
                    microchip_id=f"CHIP{random.randint(100000000, 999999999)}"
                    if random.random() > 0.3
                    else None,
                    is_deceased=False,
                    allergies="Chicken" if random.random() > 0.9 else None,
                    medical_notes="Senior pet - needs gentle handling"
                    if random.random() > 0.85
                    else None,
                    owner_first_name=owner_first,
                    owner_last_name=owner_last,
                    owner_phone=random_phone(),
                    owner_email=f"{owner_first.lower()}.{owner_last.lower()}@example.com",
                    owner_address=f"{random.randint(100, 9999)} {random.choice(['Oak', 'Maple', 'Pine', 'Cedar', 'Elm'])} {random.choice(['St', 'Ave', 'Blvd', 'Dr'])}",
                )
                session.add(patient)
                patients.append(patient)

        await session.commit()

        for patient in patients:
            await session.refresh(patient)

    print(f"  Created {len(patients)} patients")
    return patients


async def create_appointments(
    clinics: list[Clinic],
    providers: list[Provider],
    patients: list[Patient],
) -> list[Appointment]:
    """Create sample appointments."""
    print("Creating appointments...")

    appointments = []
    async with async_session_factory() as session:
        for clinic in clinics:
            clinic_providers = [
                p for p in providers if str(p.clinic_id) == str(clinic.id)
            ]
            clinic_patients = [
                p for p in patients if str(p.clinic_id) == str(clinic.id)
            ]

            if not clinic_providers or not clinic_patients:
                continue

            # Past appointments (completed, no-show, cancelled)
            for _ in range(15):
                patient = random.choice(clinic_patients)
                provider = random.choice(clinic_providers)
                start = random_datetime_range(-30, -1)
                duration = provider.default_appointment_duration_min or 30
                status = random.choices(
                    [
                        AppointmentStatus.COMPLETED,
                        AppointmentStatus.NO_SHOW,
                        AppointmentStatus.CANCELLED,
                    ],
                    weights=[0.85, 0.1, 0.05],
                )[0]

                appt = Appointment(
                    clinic_id=clinic.id,
                    patient_id=patient.id,
                    provider_id=provider.id,
                    start_time=start,
                    end_time=start + timedelta(minutes=duration),
                    duration_minutes=duration,
                    appointment_type=random.choice(list(AppointmentType)),
                    status=status,
                    source=random.choice(
                        [
                            AppointmentSource.DASHBOARD,
                            AppointmentSource.VOICE_AI,
                            AppointmentSource.ONLINE_BOOKING,
                        ]
                    ),
                    reason=random.choice(VISIT_REASONS),
                    notes="Completed without issues."
                    if status == AppointmentStatus.COMPLETED
                    else None,
                )
                session.add(appt)
                appointments.append(appt)

            # Today's appointments
            for hour in [9, 10, 11, 14, 15, 16]:
                patient = random.choice(clinic_patients)
                provider = random.choice(clinic_providers)
                start = datetime.now(UTC).replace(
                    hour=hour, minute=0, second=0, microsecond=0
                )
                duration = provider.default_appointment_duration_min or 30

                status = random.choice(
                    [
                        AppointmentStatus.SCHEDULED,
                        AppointmentStatus.CONFIRMED,
                        AppointmentStatus.CHECKED_IN,
                    ]
                )

                appt = Appointment(
                    clinic_id=clinic.id,
                    patient_id=patient.id,
                    provider_id=provider.id,
                    start_time=start,
                    end_time=start + timedelta(minutes=duration),
                    duration_minutes=duration,
                    appointment_type=random.choice(
                        [
                            AppointmentType.CHECKUP,
                            AppointmentType.VACCINATION,
                            AppointmentType.SICK_VISIT,
                        ]
                    ),
                    status=status,
                    source=AppointmentSource.DASHBOARD,
                    reason=random.choice(VISIT_REASONS),
                )
                session.add(appt)
                appointments.append(appt)

            # Future appointments
            for _ in range(20):
                patient = random.choice(clinic_patients)
                provider = random.choice(clinic_providers)
                start = random_datetime_range(1, 30)
                duration = provider.default_appointment_duration_min or 30

                appt = Appointment(
                    clinic_id=clinic.id,
                    patient_id=patient.id,
                    provider_id=provider.id,
                    start_time=start,
                    end_time=start + timedelta(minutes=duration),
                    duration_minutes=duration,
                    appointment_type=random.choice(list(AppointmentType)),
                    status=random.choice(
                        [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]
                    ),
                    source=random.choice(
                        [
                            AppointmentSource.DASHBOARD,
                            AppointmentSource.VOICE_AI,
                            AppointmentSource.ONLINE_BOOKING,
                        ]
                    ),
                    reason=random.choice(VISIT_REASONS),
                )
                session.add(appt)
                appointments.append(appt)

        await session.commit()

        for appt in appointments:
            await session.refresh(appt)

    print(f"  Created {len(appointments)} appointments")
    return appointments


async def create_call_logs(
    clinics: list[Clinic], patients: list[Patient]
) -> list[CallLog]:
    """Create sample call logs."""
    print("Creating call logs...")

    call_logs = []
    async with async_session_factory() as session:
        # Only create call logs for clinics with voice enabled
        voice_clinics = [c for c in clinics if c.voice_enabled]

        for clinic in voice_clinics:
            clinic_patients = [
                p for p in patients if str(p.clinic_id) == str(clinic.id)
            ]

            # Create sample call logs
            for _ in range(10):
                patient = (
                    random.choice(clinic_patients)
                    if clinic_patients and random.random() > 0.3
                    else None
                )
                started_at = random_datetime_range(-14, 0)
                duration = random.randint(30, 300)
                ended_at = started_at + timedelta(seconds=duration)

                outcome = random.choice(
                    [
                        CallOutcome.APPOINTMENT_BOOKED,
                        CallOutcome.APPOINTMENT_BOOKED,
                        CallOutcome.INFORMATION_PROVIDED,
                        CallOutcome.MESSAGE_TAKEN,
                        CallOutcome.TRANSFERRED_TO_STAFF,
                    ]
                )

                call_log = CallLog(
                    clinic_id=clinic.id,
                    twilio_call_sid=f"CA{uuid4().hex[:30]}",
                    direction=CallDirection.INBOUND,
                    status=CallStatus.COMPLETED,
                    outcome=outcome,
                    from_phone=patient.owner_phone if patient else random_phone(),
                    to_phone=clinic.twilio_phone_number or clinic.phone,
                    caller_name=patient.owner_full_name if patient else None,
                    patient_id_matched=str(patient.id) if patient else None,
                    started_at=started_at,
                    ended_at=ended_at,
                    duration_seconds=duration,
                    ring_duration_seconds=random.randint(2, 10),
                    ai_handled=True,
                    ai_confidence_score=round(random.uniform(0.75, 0.99), 2),
                    transcript=f"AI: Thank you for calling {clinic.name}. How can I help you today?\nCaller: I'd like to schedule an appointment for my pet.\nAI: I'd be happy to help you schedule an appointment...",
                    summary=f"Caller requested appointment scheduling. {outcome.value.replace('_', ' ').title()}.",
                    key_points=["Appointment request", outcome.value.replace("_", " ")],
                    requires_follow_up=random.random() > 0.9,
                )
                session.add(call_log)
                call_logs.append(call_log)

        await session.commit()

        for call_log in call_logs:
            await session.refresh(call_log)

    print(f"  Created {len(call_logs)} call logs")
    return call_logs


async def seed_database(clear: bool = False, minimal: bool = False) -> None:
    """Main function to seed the database."""
    print("\n" + "=" * 50)
    print("PawPoint Seed Data Script")
    print("=" * 50 + "\n")

    if clear:
        await clear_data()

    # Check if data already exists
    async with async_session_factory() as session:
        result = await session.execute(select(Clinic).limit(1))
        existing_clinic = result.scalar_one_or_none()

        if existing_clinic and not clear:
            print(
                "WARNING: Data already exists. Use --clear to remove existing data first."
            )
            print("Aborting to prevent duplicate data.\n")
            return

    # Create seed data
    users = await create_users()
    clinics = await create_clinics()
    await associate_users_clinics(users, clinics)

    if minimal:
        clinics = clinics[:1]  # Only use first clinic

    providers = await create_providers(clinics)
    patients = await create_patients(clinics, count_per_clinic=10 if minimal else 20)
    await create_appointments(clinics, providers, patients)
    await create_call_logs(clinics, patients)

    print("\n" + "=" * 50)
    print("Seed data created successfully!")
    print("=" * 50)
    print("\nSample login credentials:")
    print("  Super Admin: admin@pawpoint.dev")
    print("  Clinic Admin: dr.sarah@happypaws.dev")
    print("  Staff: mike@happypaws.dev")
    print("  Viewer: viewer@pawpoint.dev")
    print(
        "\n(Note: Passwords are placeholders - use your auth provider for actual login)"
    )
    print()


async def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Seed the PawPoint database with sample data."
    )
    parser.add_argument(
        "--clear", action="store_true", help="Clear existing data before seeding"
    )
    parser.add_argument(
        "--minimal", action="store_true", help="Create minimal seed data"
    )
    args = parser.parse_args()

    try:
        await seed_database(clear=args.clear, minimal=args.minimal)
    except Exception as e:
        print(f"\nError seeding database: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
