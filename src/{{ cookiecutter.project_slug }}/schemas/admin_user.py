from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AdminUserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminUserCreationRequest(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class AdminUserAccessTokenPayload(BaseModel):
    id: int
    username: str


class AdminUserLoginByUsernameRequest(BaseModel):
    username: str
    password: str


class AdminUserAccessTokenResponse(BaseModel):
    access_token: str
