#!/usr/bin/env python
"""
Regenerate slugs for existing clinics.

This script updates all existing clinics to have new random slugs
in the format: {adjective}-{noun}-{number}

Usage:
    cd backend
    PYTHONPATH=. uv run python scripts/regenerate_clinic_slugs.py
    PYTHONPATH=. uv run python scripts/regenerate_clinic_slugs.py --clinic-id <uuid>  # Update specific clinic
    PYTHONPATH=. uv run python scripts/regenerate_clinic_slugs.py --dry-run  # Preview changes
"""

# ruff: noqa: T201, S311 - CLI script uses print and non-crypto random for slug generation

import argparse
import asyncio
import random
from uuid import UUID

from sqlalchemy import select

from app.db import async_session_factory
from app.models.clinic import Clinic


def generate_random_slug() -> str:
    """Generate a unique, random slug.

    Format: {adjective}-{noun}-{3-digit-number}
    Example: sunny-dolphin-482
    """
    adjectives = [
        "sunny",
        "happy",
        "bright",
        "swift",
        "calm",
        "gentle",
        "lucky",
        "clever",
        "noble",
        "brave",
        "kind",
        "wise",
        "warm",
        "cool",
        "fresh",
        "pure",
        "true",
        "bold",
        "fair",
        "keen",
        "active",
        "quiet",
        "golden",
        "silver",
        "cosmic",
        "ocean",
        "sky",
        "royal",
        "elegant",
        "modern",
        "classic",
        "prime",
        "stellar",
        "vibrant",
    ]

    nouns = [
        "dolphin",
        "eagle",
        "fox",
        "owl",
        "wolf",
        "hawk",
        "lion",
        "tiger",
        "bear",
        "deer",
        "swan",
        "dove",
        "falcon",
        "raven",
        "phoenix",
        "dragon",
        "unicorn",
        "pegasus",
        "griffin",
        "lotus",
        "willow",
        "maple",
        "cedar",
        "oak",
        "pine",
        "river",
        "mountain",
        "valley",
        "meadow",
        "forest",
        "ocean",
        "harbor",
        "summit",
        "peak",
    ]

    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    number = random.randint(100, 999)

    return f"{adjective}-{noun}-{number}"


async def ensure_unique_slug(slug: str, clinic_id: UUID | None = None) -> str:
    """Ensure the slug is unique, regenerating if necessary.

    Args:
        slug: Initial slug to check
        clinic_id: Optional clinic ID to exclude from uniqueness check

    Returns:
        Unique slug
    """
    async with async_session_factory() as db:
        max_attempts = 50
        for _ in range(max_attempts):
            query = select(Clinic).where(Clinic.slug == slug)
            if clinic_id:
                query = query.where(Clinic.id != clinic_id)

            result = await db.execute(query)
            if not result.scalar_one_or_none():
                return slug

            # Slug exists, generate a new one
            slug = generate_random_slug()

        raise RuntimeError(
            f"Failed to generate unique slug after {max_attempts} attempts"
        )


async def regenerate_all_slugs(dry_run: bool = False) -> None:
    """Regenerate slugs for all clinics.

    Args:
        dry_run: If True, only print changes without updating database
    """
    async with async_session_factory() as db:
        # Get all clinics
        result = await db.execute(select(Clinic))
        clinics = result.scalars().all()

        if not clinics:
            print("No clinics found.")
            return

        print(f"\nFound {len(clinics)} clinic(s)\n")

        updates = []
        for clinic in clinics:
            old_slug = clinic.slug
            new_slug = generate_random_slug()
            new_slug = await ensure_unique_slug(new_slug, clinic.id)

            updates.append((clinic, old_slug, new_slug))

            print(f"Clinic: {clinic.name}")
            print(f"  Old slug: {old_slug}")
            print(f"  New slug: {new_slug}")
            print()

        if dry_run:
            print("DRY RUN - No changes made to database")
            return

        # Confirm before proceeding
        response = input(f"\nUpdate {len(updates)} clinic slug(s)? (yes/no): ").lower()
        if response != "yes":
            print("Cancelled.")
            return

        # Apply updates
        for clinic, _old_slug, new_slug in updates:
            clinic.slug = new_slug

        await db.commit()
        print(f"\n✅ Successfully updated {len(updates)} clinic slug(s)")


async def regenerate_clinic_slug(clinic_id: UUID, dry_run: bool = False) -> None:
    """Regenerate slug for a specific clinic.

    Args:
        clinic_id: Clinic UUID
        dry_run: If True, only print changes without updating database
    """
    async with async_session_factory() as db:
        result = await db.execute(select(Clinic).where(Clinic.id == clinic_id))
        clinic = result.scalar_one_or_none()

        if not clinic:
            print(f"❌ Clinic with ID {clinic_id} not found")
            return

        old_slug = clinic.slug
        new_slug = generate_random_slug()
        new_slug = await ensure_unique_slug(new_slug, clinic.id)

        print(f"\nClinic: {clinic.name}")
        print(f"  Old slug: {old_slug}")
        print(f"  New slug: {new_slug}")
        print()

        if dry_run:
            print("DRY RUN - No changes made to database")
            return

        # Confirm
        response = input("Update this clinic's slug? (yes/no): ").lower()
        if response != "yes":
            print("Cancelled.")
            return

        # Apply update
        clinic.slug = new_slug
        await db.commit()
        print(f"\n✅ Successfully updated slug for {clinic.name}")


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Regenerate clinic slugs with random unique identifiers"
    )
    parser.add_argument(
        "--clinic-id",
        type=str,
        help="Update slug for specific clinic ID (UUID)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without updating database",
    )

    args = parser.parse_args()

    if args.clinic_id:
        try:
            clinic_uuid = UUID(args.clinic_id)
            await regenerate_clinic_slug(clinic_uuid, dry_run=args.dry_run)
        except ValueError:
            print(f"❌ Invalid UUID: {args.clinic_id}")
    else:
        await regenerate_all_slugs(dry_run=args.dry_run)


if __name__ == "__main__":
    asyncio.run(main())
