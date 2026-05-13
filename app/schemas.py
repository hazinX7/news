from pydantic import BaseModel, EmailStr


class RegisterForm(BaseModel):
    name: str
    email: EmailStr
    password: str

