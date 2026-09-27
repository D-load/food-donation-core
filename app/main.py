from datetime import datetime, timezone
from typing import Annotated, List
from fastapi import FastAPI, Depends, status
from app.models import (
    DonationItemCreate,
    DonationItemResponse,
    UserRole,
    TokenResponse,
)
from app.auth import get_current_user, RoleGuard, create_access_token

app = FastAPI(
    title="Sistema de Donaciones y Recursos Alimentarios",
    version="1.0.0",
    description="API de intercambio de recursos entre empresas donantes y organizaciones sociales"
)

# Persistencia simulada
donations_db: List[dict] = []
donation_counter = 1

allow_donors = RoleGuard([UserRole.DONOR_COMPANY, UserRole.ADMIN])
allow_all_authenticated = RoleGuard([UserRole.ADMIN, UserRole.DONOR_COMPANY, UserRole.SOCIAL_ORG])

@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.post("/token", response_model=TokenResponse)
def login(username: str, role: UserRole):
    token = create_access_token({"sub": username, "role": role.value})
    return {"access_token": token, "token_type": "bearer"}

@app.post(
    "/donations",
    response_model=DonationItemResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_donors)],
)
@app.post(
    "/donations/",
    response_model=DonationItemResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_donors)],
)
def register_donation(
    donation: DonationItemCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    global donation_counter
    record = donation.model_dump()
    record.update({
        "id": donation_counter,
        "donor_company": current_user["username"],
        "status": "disponible",
        "created_at": datetime.now(timezone.utc),
    })
    donation_counter += 1
    donations_db.append(record)
    return record

@app.get(
    "/donations",
    response_model=List[DonationItemResponse],
    dependencies=[Depends(allow_all_authenticated)],
)
@app.get(
    "/donations/",
    response_model=List[DonationItemResponse],
    dependencies=[Depends(allow_all_authenticated)],
)
def list_available_donations():
    return [d for d in donations_db if d["status"] == "disponible"]