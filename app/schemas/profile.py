from typing import Optional

from pydantic import BaseModel

from app.schemas.user import UserUpdate
from app.schemas.vendor import VendorUpdate


class ProfileUpdate(BaseModel):
    user: Optional[UserUpdate] = None
    vendor: Optional[VendorUpdate] = None
