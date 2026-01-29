"""Authentication service for clinic registration and login."""

import asyncio
import random
import re
import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.clinic import Clinic
from app.models.user import User, UserRole, user_clinic_association
from app.services.clinic import DEFAULT_VOICE_SETTINGS


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register_clinic(
        self,
        clinic_name: str,
        email: str,
        password: str,
        admin_first_name: str | None = None,
        admin_last_name: str | None = None,
    ) -> tuple[User, Clinic, str]:
        """
        Register a new clinic with an admin user.

        Args:
            clinic_name: Name of the clinic
            email: Admin user's email
            password: Admin user's password
            admin_first_name: Optional first name for admin user
            admin_last_name: Optional last name for admin user

        Returns:
            Tuple of (user, clinic, access_token)

        Raises:
            ValueError: If email already exists or validation fails
        """
        # Check if email already exists
        existing_user = await self.db.execute(select(User).where(User.email == email))
        if existing_user.scalar_one_or_none():
            # Generic error message to prevent username enumeration
            raise ValueError(
                "Registration failed. Please check your information and try again."
            )

        # Generate a unique slug from clinic name
        slug = self._generate_slug(clinic_name)

        # Check if slug already exists and make it unique
        slug = await self._ensure_unique_slug(slug)

        # Create the clinic with default chatbot settings
        clinic = Clinic(
            name=clinic_name,
            slug=slug,
            email=email,
            voice_settings=DEFAULT_VOICE_SETTINGS.copy(),  # Initialize with defaults
        )
        self.db.add(clinic)
        await self.db.flush()

        # Create the admin user with provided or default names
        user = User(
            email=email,
            password_hash=hash_password(password),
            first_name=admin_first_name or "Clinic",
            last_name=admin_last_name or "Administrator",
            role=UserRole.ADMIN,
        )
        self.db.add(user)
        await self.db.flush()

        # Associate user with clinic
        await self.db.execute(
            user_clinic_association.insert().values(
                user_id=user.id,
                clinic_id=clinic.id,
            )
        )

        # Generate access token
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "clinic_id": str(clinic.id),
                "role": user.role.value,
            }
        )

        return user, clinic, access_token

    async def login(self, email: str, password: str) -> tuple[User, Clinic, str]:
        """
        Authenticate a user and return tokens.

        Uses constant-time verification to prevent timing attacks.

        Args:
            email: User's email
            password: User's password

        Returns:
            Tuple of (user, clinic, access_token)

        Raises:
            ValueError: If credentials are invalid
        """
        # Find user by email
        result = await self.db.execute(
            select(User).where(User.email == email, User.is_active == True)  # noqa: E712
        )
        user = result.scalar_one_or_none()

        # Always perform password verification to prevent timing attacks
        # Use a dummy hash if user doesn't exist to maintain constant time
        dummy_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7k8TvQW.jW"
        password_hash = (
            user.password_hash if user and user.password_hash else dummy_hash
        )

        # This takes constant time regardless of whether user exists
        password_valid = verify_password(password, password_hash)

        # Check all conditions together at the end
        if not user or not user.password_hash or not password_valid:
            # Add a small random delay to further mask timing differences
            await asyncio.sleep(random.uniform(0.05, 0.15))  # noqa: S311
            raise ValueError("Invalid email or password")

        # Get user's clinic (first one for now)
        if not user.clinics:
            raise ValueError("User has no associated clinic")

        clinic = user.clinics[0]

        # Generate access token
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "clinic_id": str(clinic.id),
                "role": user.role.value,
            }
        )

        return user, clinic, access_token

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Get a user by their ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_active == True)  # noqa: E712
        )
        return result.scalar_one_or_none()

    def _generate_slug(self, name: str) -> str:
        """Generate a URL-friendly slug from a name."""
        # Convert to lowercase and replace spaces with hyphens
        slug = name.lower().strip()
        # Remove special characters
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        # Replace spaces with hyphens
        slug = re.sub(r"\s+", "-", slug)
        # Remove multiple consecutive hyphens
        slug = re.sub(r"-+", "-", slug)
        # Remove leading/trailing hyphens
        slug = slug.strip("-")

        # If slug is empty or too short after processing, generate a default
        if not slug or len(slug) < 2:
            slug = f"clinic-{str(uuid.uuid4())[:8]}"

        return slug

    async def _ensure_unique_slug(self, slug: str) -> str:
        """Ensure the slug is unique, appending a number if necessary."""
        base_slug = slug
        counter = 1

        while True:
            result = await self.db.execute(select(Clinic).where(Clinic.slug == slug))
            if not result.scalar_one_or_none():
                return slug
            slug = f"{base_slug}-{counter}"
            counter += 1
