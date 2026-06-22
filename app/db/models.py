from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

ESCALATION_REASONS = ("ask-human-support", "out-of-knowledge", "emergency")


class Customer(Base):
    __tablename__ = "customer"

    cust_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cust_name: Mapped[str] = mapped_column(String, nullable=False)
    contact: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    addr: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)

    policies: Mapped[list["Policy"]] = relationship(back_populates="customer")
    call_logs: Mapped[list["CallLog"]] = relationship(back_populates="customer")
    escalations: Mapped[list["EscalationLog"]] = relationship(back_populates="customer")


class Policy(Base):
    __tablename__ = "policy"
    __table_args__ = (
        CheckConstraint("tier IN ('silver', 'gold', 'diamond', 'platinum')"),
    )

    policy_num: Mapped[str] = mapped_column(String, primary_key=True)
    cust_id: Mapped[int] = mapped_column(Integer, ForeignKey("customer.cust_id"))
    tier: Mapped[str] = mapped_column(String, nullable=False)
    premium_status: Mapped[str] = mapped_column(String, nullable=False)
    premium_amt: Mapped[float] = mapped_column(Integer, nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="policies")
    claims: Mapped[list["Claim"]] = relationship(back_populates="policy")


class Claim(Base):
    __tablename__ = "claim"

    claim_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_num: Mapped[str] = mapped_column(String, ForeignKey("policy.policy_num"))
    status: Mapped[str] = mapped_column(String, nullable=False)
    docs_required: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)

    policy: Mapped["Policy"] = relationship(back_populates="claims")


class CallLog(Base):
    __tablename__ = "call_log"

    call_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cust_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("customer.cust_id"), nullable=True
    )
    caller_name: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str] = mapped_column(String, nullable=False)
    sentiment: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[str] = mapped_column(String, nullable=False)
    end_time: Mapped[str] = mapped_column(String, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)

    customer: Mapped["Customer | None"] = relationship(back_populates="call_logs")


class EscalationLog(Base):
    __tablename__ = "escalation_log"
    __table_args__ = (
        CheckConstraint(f"reason IN {ESCALATION_REASONS}"),
    )

    esc_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cust_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("customer.cust_id"), nullable=True
    )
    reason: Mapped[str] = mapped_column(String, nullable=False)
    note: Mapped[str] = mapped_column(String, nullable=False, default="")
    created_at: Mapped[str] = mapped_column(String, nullable=False)

    customer: Mapped["Customer | None"] = relationship(back_populates="escalations")
