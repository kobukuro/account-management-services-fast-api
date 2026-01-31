from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from .user import User
from .authentication_type import AuthenticationType


class UserAuthentication(Base):
    __tablename__ = "user_authentication"
    __table_args__ = (UniqueConstraint("type", "email", name="uq_type_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False
    )
    type: Mapped[AuthenticationType] = mapped_column(
        Enum(AuthenticationType), nullable=False
    )
    provider_id: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str | None] = mapped_column(String, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship("User", back_populates="authentications")

    def __init__(
            self,
            user: User,
            authn_type: AuthenticationType,
            email: str,
            password: str | None = None,
            provider_id: str | None = None,
    ):
        super().__init__()
        self.user = user
        self.type = authn_type
        self.email = email

        if type == AuthenticationType.LOCAL:
            if not password or not password.strip():
                raise ValueError(
                    "Password cannot be null or empty for local authentication."
                )
            self.password = password
            self.enabled = False
        else:
            self.provider_id = provider_id
            self.password = None
            self.enabled = True

    @classmethod
    def create_local_auth(
            cls, user: User, email: str, password: str
    ) -> "UserAuthentication":
        return cls(user=user, authn_type=AuthenticationType.LOCAL, email=email, password=password)
