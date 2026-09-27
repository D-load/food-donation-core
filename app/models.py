from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    ADMIN = "administrador"
    DONOR_COMPANY = "empresa_donante"
    SOCIAL_ORG = "organizacion_social"


class FoodCategory(str, Enum):
    PERISHABLE = "perecedero"
    NON_PERISHABLE = "no_perecedero"
    PREPARED = "alimento_preparado"


class DonationItemCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120, description="Ej. Lote de verduras frescas")
    category: FoodCategory
    quantity_kg: float = Field(..., gt=0.0, description="Peso en kilogramos debe ser mayor a 0")
    expiration_date: date
    requires_refrigeration: bool = False
    pickup_address: str = Field(..., min_length=5, max_length=200)


class DonationItemResponse(DonationItemCreate):
    id: int
    donor_company: str
    status: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class Donation(BaseModel):
    food_name: str
    quantity: int
    donor_name: str
    location: str

    model_config = {"extra": "ignore"}
