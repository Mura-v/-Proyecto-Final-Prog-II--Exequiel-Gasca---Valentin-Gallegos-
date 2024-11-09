from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreateSchema(BaseModel):
    user_name : str 
    password : str
    email : EmailStr
    image_url : Optional[str] = None