"""
User Model

Represents system users (clinic staff, admins) with role-based access control.
Users can belong to multiple clinics through the UserClinic association.
"""

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.clinic import Clinic


class UserRole(StrEnum):
    """User roles for access control."""

    SUPER_ADMIN = "super_admin"  # Platform admin (can manage all clinics)
    ADMIN = "admin"  # Clinic admin (full access to their clinic)
    STAFF = "staff"  # Clinic staff (can manage patients, appointments)
    VIEWER = "viewer"  # Read-only access


# Association table for User <-> Clinic many-to-many relationship
user_clinic_association = Table(
    "user_clinic_associations",
    Base.metadata,
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "clinic_id",
        UUID(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base, TimestampMixin, SoftDeleteMixin):
    """
    System user model.

    Users can have different roles and belong to multiple clinics.
    External auth provider ID (e.g., Clerk) is stored for SSO integration.
    """

    __tablename__ = "users"

    # Profile fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,  # Null if using external auth
    )

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Role and permissions
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=lambda x: [e.value for e in x]),
        default=UserRole.STAFF,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    # External auth provider (Clerk, Auth0, etc.)
    external_auth_provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Auth provider name (clerk, auth0, etc.)",
    )
    external_auth_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
        comment="User ID from external auth provider",
    )

    # Login tracking
    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    clinics: Mapped[list["Clinic"]] = relationship(
        secondary=user_clinic_association,
        back_populates="users",
        lazy="selectin",
    )

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    def has_clinic_access(self, clinic_id: str) -> bool:
        """Check if user has access to a specific clinic."""
        if self.role == UserRole.SUPER_ADMIN:
            return True
        return any(str(c.id) == clinic_id for c in self.clinics)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
