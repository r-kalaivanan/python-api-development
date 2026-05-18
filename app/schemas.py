from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, Literal

class CreateUser(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PostBase(BaseModel):
    title: str 
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    published: bool

class PostResponse(PostBase):
    id: int
    published: bool
    created_at: datetime
    owner: UserResponse

    model_config = ConfigDict(from_attributes=True)

class PostVoteResponse(BaseModel):
    post: PostResponse
    votes: int

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int]

class Vote(BaseModel):
    post_id: int
    vote_dir: Literal[0, 1]