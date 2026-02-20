from enum import Enum
from pydantic import BaseModel, Field


class OptionType(str, Enum):
    CALL = "Call"
    PUT = "Put"


class FXOption(BaseModel):

    id: str
    option_type: OptionType = Field(description="Option type: put or call")
    strike: float = Field(gt=0, description="Strike price of the option")
    volatility: float = Field(gt=0, description="Volatility of the underlying asset")
    time_to_maturity: float = Field(ge=0, description="Time to maturity of the option")
    spot_price: float = Field(gt=0, description="Spot price of the underlying asset")
    domestic_rate: float = Field(description="Domestic interest rate")
    foreign_rate: float = Field(description="Foreign interest rate")
    underlying: str = Field(description="Currency pair")
    notional: float = Field(gt=0, description="Notional amount")
    notional_currency: str = Field(description="Currency of the notional amount")
