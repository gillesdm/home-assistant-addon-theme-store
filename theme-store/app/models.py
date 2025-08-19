from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


class Theme(BaseModel):
    id: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9_\-\.]+$")
    name: str = Field(min_length=1, max_length=120)
    author: Optional[str] = Field(default=None, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    # Optional assets for the future (previews, source)
    homepage: Optional[HttpUrl] = None
    preview_image: Optional[HttpUrl] = None


class ThemeCreate(BaseModel):
    id: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9_\-\.]+$")
    name: str = Field(min_length=1, max_length=120)
    author: Optional[str] = Field(default=None, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    homepage: Optional[HttpUrl] = None
    preview_image: Optional[HttpUrl] = None


class DeleteResult(BaseModel):
    status: Literal["deleted"]
