from pydantic import BaseModel, Field

class BrandOut(BaseModel):
    id: int
    slug: str
    name: str
    country: str | None = None

    model_config = {"from_attributes": True}

class BrandCreate(BaseModel):
    slug: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=120)
    country: str | None = Field(default=None, max_length=2)
