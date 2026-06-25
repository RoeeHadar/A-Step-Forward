"""Private lesson booking requests."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from ..core.db import get_db
from ..core.rate_limit import per_ip
from ..core.settings import get_settings
from ..stores import content_store

router = APIRouter(prefix="/v1/bookings", tags=["bookings"])

HOURLY_RATE_ILS = 150


class BookingRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    phone: str | None = Field(default=None, max_length=40)
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: str = Field(pattern=r"^\d{2}:\d{2}$")
    duration_h: float = Field(ge=1, le=3)
    subject: str = Field(min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=2000)


async def require_booking_secret(
    x_booking_secret: str | None = Header(default=None, alias="X-Booking-Secret"),
) -> None:
    expected = get_settings().booking_api_secret
    if expected and x_booking_secret != expected:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("")
async def create_booking(
    body: BookingRequest,
    session=Depends(get_db),
    _secret=Depends(require_booking_secret),
    _rl=Depends(per_ip("bookings.create", per_min=10)),
) -> dict:
    price_ils = int(HOURLY_RATE_ILS * body.duration_h)
    booking_id = await content_store.insert_booking(
        session,
        name=body.name,
        email=body.email,
        phone=body.phone,
        date=body.date,
        time=body.time,
        duration_h=body.duration_h,
        subject=body.subject,
        notes=body.notes,
        price_ils=price_ils,
    )
    return {"ok": True, "id": booking_id, "price_ils": price_ils}
