from pydantic import BaseModel


class Theme(BaseModel):
    id: str
    name: str
    author: str | None = None
    description: str | None = None