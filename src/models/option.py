from pydantic import BaseModel


class FXOption(BaseModel):
    id: str
    option_type: str
    strike: float
    volatility: float
    risk_free_rate: float
    time_to_maturity: float
    spot_price: float
