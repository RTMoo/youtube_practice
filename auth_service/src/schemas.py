from pydantic import BaseModel, EmailStr, Field


class EmailSchema(BaseModel):
    email: EmailStr


class UserLoginSchema(BaseModel):
    username: str = Field(min_length=3, max_length=16)
    password: str = Field(min_length=8, max_length=255)


class UserSchema(EmailSchema):
    username: str | None = Field(min_length=3, max_length=16)
    password: str | None = Field(min_length=8, max_length=255)


class SetCredentialsSchema(UserLoginSchema):
    pass


class EmailMessage(EmailSchema):
    message: str


class SendCodeSchema(EmailSchema):
    code: str


class VerifyEmailSchema(SendCodeSchema):
    pass


class ChangePasswordSchema(BaseModel):
    old_password: str = Field(min_length=8, max_length=255)
    new_password: str = Field(min_length=8, max_length=255)


class ResetPasswordSchema(BaseModel):
    new_password: str = Field(min_length=8, max_length=255)
