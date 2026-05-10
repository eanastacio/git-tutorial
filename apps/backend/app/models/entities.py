from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    saved_companies: Mapped[list["SavedCompany"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    normalized_name: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    display_name: Mapped[str] = mapped_column(String(255), index=True)
    total_filings: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    total_certified: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    sponsorship_score: Mapped[float] = mapped_column(Numeric(6, 2), default=0, server_default="0")
    headquarters: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latest_filing_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    lcas: Mapped[list["LCARecord"]] = relationship(back_populates="company")
    saved_by_users: Mapped[list["SavedCompany"]] = relationship(back_populates="company")

    __table_args__ = (
        Index("ix_companies_filings_score", "total_filings", "sponsorship_score"),
    )


class LCARecord(Base):
    __tablename__ = "lcas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    case_number: Mapped[str] = mapped_column(String(128), index=True)
    job_title: Mapped[str] = mapped_column(String(255), index=True)
    soc_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    city: Mapped[str] = mapped_column(String(128), index=True)
    state: Mapped[str] = mapped_column(String(2), index=True)
    wage: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    wage_unit: Mapped[str | None] = mapped_column(String(64), nullable=True)
    filing_year: Mapped[int] = mapped_column(Integer, index=True)
    filing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    case_status: Mapped[str] = mapped_column(String(64), index=True)
    visa_class: Mapped[str] = mapped_column(String(32), index=True)
    worksite_location: Mapped[str] = mapped_column(String(255))
    is_internship_role: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    is_new_grad_role: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    remote_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    record_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped["Company"] = relationship(back_populates="lcas")

    __table_args__ = (
        Index("ix_lcas_filter_location_year", "state", "city", "filing_year"),
        Index("ix_lcas_company_year_status", "company_id", "filing_year", "case_status"),
        Index("ix_lcas_job_title_year", "job_title", "filing_year"),
    )


class SavedCompany(Base):
    __tablename__ = "saved_companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="saved_companies")
    company: Mapped["Company"] = relationship(back_populates="saved_by_users")

    __table_args__ = (UniqueConstraint("user_id", "company_id", name="uq_saved_company_user_company"),)


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_year: Mapped[int] = mapped_column(Integer, index=True)
    source_url: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), index=True)
    records_processed: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    records_failed: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    failures: Mapped[list["IngestionFailure"]] = relationship(back_populates="job", cascade="all, delete-orphan")


class IngestionFailure(Base):
    __tablename__ = "ingestion_failures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("ingestion_jobs.id", ondelete="CASCADE"), index=True)
    reason: Mapped[str] = mapped_column(String(512))
    raw_payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job: Mapped["IngestionJob"] = relationship(back_populates="failures")
