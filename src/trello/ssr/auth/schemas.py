from pydantic import BaseModel


class SignInFormData(BaseModel):
    email: str
    password: str


class SignUpFormData(BaseModel):
    email: str
    username: str
    password: str
    confirm: str
