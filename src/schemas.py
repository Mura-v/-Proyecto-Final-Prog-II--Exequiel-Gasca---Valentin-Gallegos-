from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreateSchema(BaseModel):
    user_name : str 
    password : str
    email : EmailStr
    image_url : Optional[str] = None

class PostCreateSchema(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None