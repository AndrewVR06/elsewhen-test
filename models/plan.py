from pydantic import BaseModel, field_validator, Field, condecimal
from .metals import Metals
from decimal import Decimal, ROUND_HALF_EVEN


class Plan(BaseModel):
    plan_id: str
    state: str
    metal_level: Metals
    rate: condecimal(gt=0)
    rate_area: int = Field(..., ge=0)

    @field_validator('state')
    def validate_state(cls, state: str):
        if len(state) != 2:
            raise ValueError("state must be a 2 letter abbreviation")
        return state.lower()

    @field_validator('metal_level', mode='before')
    def validate_metal_level(cls, metal_level: str):
        metal_level = metal_level.lower()
        if metal_level not in Metals.get_values():
            raise ValueError(f"Plan is not a valid metal plan! Allowed values are {Metals.get_values()}")
        return metal_level

    @field_validator('rate', mode='after')
    def validate_rate(cls, rate: Decimal):
        return rate.quantize(Decimal("1.00"), rounding=ROUND_HALF_EVEN)  # use bankers rounding
