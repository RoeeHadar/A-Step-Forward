"""Private lesson booking requests."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field

from ..core.db import get_db
from ..stores import content_store

router = APIRouter(prefix="/v1/bookings", tags=["bookings"])

HOURLY_RATE_ILS = 150


class BookingRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=40)
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: str = Field(pattern=r"^\d{2}:\d{2}$")
    duration_h: float = Field(ge=1, le=3)
    subject: str = Field(min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=2000)


@router.post("")
async def create_booking(body: BookingRequest, session=Depends(get_db)) -> dict:
    price_ils = int(HOURLY_RATE_ILS * body.duration_h)
    booking_id = await content_store.insert_booking(
        session,
        name=body.name,
        email=str(body.email),
        phone=body.phone,
        date=body.date,
        time=body.time,
        duration_h=body.duration_h,
        subject=body.subject,
        notes=body.notes,
        price_ils=price_ils,
    )
    return {"ok": True, "id": booking_id, "price_ils": price_ils}
