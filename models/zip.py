from pydantic import BaseModel, field_validator, Field


class Zip(BaseModel):
    zipcode: int = Field(..., ge=0)
    state: str
    county_code: int = Field(..., ge=0)
    name: str
    rate_area: int = Field(..., ge=0)

    @field_validator('state')
    def validate_state(cls, state: str):
        if len(state) != 2:
            raise ValueError("state must be a 2 letter abbreviation")
        return state.lower()
