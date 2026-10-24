"""Pydantic request/response and tool-contract schemas."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=256)

class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(gt=0)

class HelpdeskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=5, max_length=4000, description="Describe the IT issue")
    session_id: str | None = Field(default=None, max_length=100)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("query must not be blank")
        return value

class HelpdeskResponse(BaseModel):
    session_id: str
    user_id: str
    final_answer: str
    decision: str
    needs_approval: bool = False
    ticket: dict | None = None
    tool_results: list[dict] = Field(default_factory=list)

class TicketCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=5, max_length=4000)
    user_id: str = Field(min_length=1, max_length=100)
