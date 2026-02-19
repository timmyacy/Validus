import pytest
from pydantic import ValidationError
from src.models.option import FXOption, OptionType
from src.models.result import PortfolioSummary
from src.pricing.black_scholes import BlackScholesFX


def test_call_positive_delta():
    option = FXOption(id="CALL001",option_type=OptionType.CALL,spot_price=1.1,strike=1.12,volatility=0.15,domestic_rate=0.02,
        foreign_rate=0.01,time_to_maturity=0.25,underlying="EUR/USD",notional=1000000,notional_currency="USD")

    delta = BlackScholesFX.calculate_delta(option)
    assert delta > 0, f"Call delta should be positive, calculated delta is {delta}"


def test_put_negative_delta():
    option = FXOption(id="PUT001",option_type=OptionType.PUT,spot_price=1.1,strike=1.15,volatility=0.12,domestic_rate=0.02,
        foreign_rate=0.01,time_to_maturity=0.5,underlying="EUR/USD",notional=500000,notional_currency="USD")

    delta = BlackScholesFX.calculate_delta(option)

    assert delta < 0, f"Put delta should be negative, calculated delta is {delta}"


def test_positive_vega():
    call = FXOption(id="CALL001",option_type=OptionType.CALL,spot_price=1.1,strike=1.12,volatility=0.15,domestic_rate=0.02,
        foreign_rate=0.01,time_to_maturity=0.25,underlying="EUR/USD",notional=1000000,notional_currency="USD")

    put = FXOption(id="PUT001",option_type=OptionType.PUT,spot_price=1.1,strike=1.15,volatility=0.12,domestic_rate=0.02,
        foreign_rate=0.01,time_to_maturity=0.5,underlying="EUR/USD",notional=500000,notional_currency="USD")

    call_vega = BlackScholesFX.calculate_vega(call)
    put_vega = BlackScholesFX.calculate_vega(put)

    assert call_vega > 0, f"Call vega should be positive, calculated vega for call: {call_vega}"
    assert put_vega > 0, f"Put vega should be positive, calculated vega for put: {put_vega}"


def test_negative_volatility():

    with pytest.raises(ValidationError) as exc_info:
        FXOption(id="inv_CALL01",option_type=OptionType.CALL,spot_price=1.1,strike=1.12,volatility=-0.15,domestic_rate=0.02,
            foreign_rate=0.01,time_to_maturity=0.25,underlying="EUR/USD",notional=1000000,notional_currency="USD")

    assert "volatility" in str(exc_info.value).lower()



def test_portfolio_summation():

    call = FXOption(id="CALL001",option_type=OptionType.CALL,spot_price=1.1,strike=1.12,volatility=0.15,domestic_rate=0.02,
        foreign_rate=0.01,time_to_maturity=0.25,underlying="EUR/USD",notional=1000000,notional_currency="USD")

    put = FXOption(id="PUT001",option_type=OptionType.PUT,spot_price=1.1,strike=1.15,volatility=0.12,domestic_rate=0.02,
        foreign_rate=0.01,time_to_maturity=0.5,underlying="EUR/USD",notional=500000,notional_currency="USD")

    result1 = BlackScholesFX.calculate_greeks_and_pv(call)
    result2 = BlackScholesFX.calculate_greeks_and_pv(put)

    total_pv = result1.pv + result2.pv
    total_delta = result1.delta + result2.delta
    total_vega = result1.vega + result2.vega

    summary = PortfolioSummary(total_pv= total_pv,total_delta= total_delta,total_vega= total_vega,num_of_trades=2)

    assert summary.total_pv == pytest.approx(total_pv)
    assert summary.total_delta == pytest.approx(total_delta)
    assert summary.total_vega == pytest.approx(total_vega)
    assert summary.num_of_trades == 2