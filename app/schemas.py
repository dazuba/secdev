from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class FeatureBase(BaseModel):
    title: str
    desc: Optional[str] = None


class FeatureCreate(FeatureBase):
    pass


class FeatureUpdate(BaseModel):
    title: Optional[str] = None
    desc: Optional[str] = None


class FeatureResponse(FeatureBase):
    id: int
    owner_id: int
    created_at: datetime
    vote_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class VoteCreate(BaseModel):
    value: int


class VoteResponse(BaseModel):
    id: int
    value: int
    feature_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
