import math

import pytest
from pydantic import ValidationError
from src.models.option import FXOption, OptionType
from src.models.result import PortfolioSummary
from src.pricing.black_scholes import BlackScholesFX
import numpy as np


def test_pv_non_negative():
    """Ensures that option prices remain non-negative."""
    option = FXOption(
        id="CALL001",
        option_type=OptionType.CALL,
        spot_price=1.1,
        strike=1.12,
        volatility=0.15,
        domestic_rate=0.02,
        foreign_rate=0.01,
        time_to_maturity=0.25,
        underlying="EUR/USD",
        notional=1000000,
        notional_currency="USD",
    )

    result = BlackScholesFX.calculate_greeks_and_pv(option)
    assert result.pv >= 0, f"PV should be non-negative, calculated PV is {result.pv}"


def test_call_positive_delta():
    """Call delta should be positive"""
    option = FXOption(
        id="CALL001",
        option_type=OptionType.CALL,
        spot_price=1.1,
        strike=1.12,
        volatility=0.15,
        domestic_rate=0.02,
        foreign_rate=0.01,
        time_to_maturity=0.25,
        underlying="EUR/USD",
        notional=1000000,
        notional_currency="USD",
    )
    d1, _ = BlackScholesFX.calculate_d1_d2(option)
    multiplier = BlackScholesFX.get_notional(option)
    delta = BlackScholesFX.calculate_delta(option, d1, multiplier)
    assert delta > 0, f"Call delta should be positive, calculated delta is {delta}"


def test_put_negative_delta():
    """Put delta should be negative"""
    option = FXOption(
        id="PUT001",
        option_type=OptionType.PUT,
        spot_price=1.1,
        strike=1.15,
        volatility=0.12,
        domestic_rate=0.02,
        foreign_rate=0.01,
        time_to_maturity=0.5,
        underlying="EUR/USD",
        notional=500000,
        notional_currency="USD",
    )
    d1, _ = BlackScholesFX.calculate_d1_d2(option)
    multiplier = BlackScholesFX.get_notional(option)
    delta = BlackScholesFX.calculate_delta(option, d1, multiplier)
    assert delta < 0, f"Put delta should be negative, calculated delta is {delta}"


def test_positive_vega():
    """Vega should be positive for calls and puts"""
    call = FXOption(
        id="CALL001",
        option_type=OptionType.CALL,
        spot_price=1.1,
        strike=1.12,
        volatility=0.15,
        domestic_rate=0.02,
        foreign_rate=0.01,
        time_to_maturity=0.25,
        underlying="EUR/USD",
        notional=1000000,
        notional_currency="USD",
    )

    put = FXOption(
        id="PUT001",
        option_type=OptionType.PUT,
        spot_price=1.1,
        strike=1.15,
        volatility=0.12,
        domestic_rate=0.02,
        foreign_rate=0.01,
        time_to_maturity=0.5,
        underlying="EUR/USD",
        notional=500000,
        notional_currency="USD",
    )
    d1_call, _ = BlackScholesFX.calculate_d1_d2(call)
    d1_put, _ = BlackScholesFX.calculate_d1_d2(put)
    multiplier_call = BlackScholesFX.get_notional(call)
    multiplier_put = BlackScholesFX.get_notional(put)
    call_vega = BlackScholesFX.calculate_vega(call, d1_call, multiplier_call)
    put_vega = BlackScholesFX.calculate_vega(put, d1_put, multiplier_put)

    assert (
        call_vega > 0
    ), f"Call vega should be positive, calculated vega for call: {call_vega}"
    assert (
        put_vega > 0
    ), f"Put vega should be positive, calculated vega for put: {put_vega}"


def test_negative_volatility():
    """Negative volatility should raise ValidationError"""
    with pytest.raises(ValidationError):
        FXOption(
            id="inv_CALL01",
            option_type=OptionType.CALL,
            spot_price=1.1,
            strike=1.12,
            volatility=-0.15,
            domestic_rate=0.02,
            foreign_rate=0.01,
            time_to_maturity=0.25,
            underlying="EUR/USD",
            notional=1000000,
            notional_currency="USD",
        )


def test_missing_field_option():
    """Missing required field should raise ValidationError"""
    with pytest.raises(ValidationError):
        FXOption(
            id="CALL001",
            option_type=OptionType.CALL,
            spot_price=1.1,
            volatility=0.15,
            domestic_rate=0.02,
            foreign_rate=0.01,
            time_to_maturity=0.25,
            underlying="EUR/USD",
            notional=1000000,
            notional_currency="USD",
        )


def test_portfolio_summation():
    """Portfolio totals should equal sum of individual trades"""
    call = FXOption(
        id="CALL001",
        option_type=OptionType.CALL,
        spot_price=1.1,
        strike=1.12,
        volatility=0.15,
        domestic_rate=0.02,
        foreign_rate=0.01,
        time_to_maturity=0.25,
        underlying="EUR/USD",
        notional=1000000,
        notional_currency="USD",
    )

    put = FXOption(
        id="PUT001",
        option_type=OptionType.PUT,
        spot_price=1.1,
        strike=1.15,
        volatility=0.12,
        domestic_rate=0.02,
        foreign_rate=0.01,
        time_to_maturity=0.5,
        underlying="EUR/USD",
        notional=500000,
        notional_currency="USD",
    )

    result1 = BlackScholesFX.calculate_greeks_and_pv(call)
    result2 = BlackScholesFX.calculate_greeks_and_pv(put)

    total_pv = result1.pv + result2.pv
    total_delta = result1.delta + result2.delta
    total_vega = result1.vega + result2.vega

    summary = PortfolioSummary(
        total_pv=total_pv,
        total_delta=total_delta,
        total_vega=total_vega,
        num_of_trades=2,
    )

    assert summary.total_pv == pytest.approx(total_pv)
    assert summary.total_delta == pytest.approx(total_delta)
    assert summary.total_vega == pytest.approx(total_vega)
    assert summary.num_of_trades == 2


def test_put_call_parity():
    """
    Test for put call parity on a trade.
    """

    call = FXOption(
        id="T000001",
        underlying="EUR/USD",
        notional=1000000,
        notional_currency="USD",
        spot_price=1.1,
        strike=1.12,
        volatility=0.11,
        domestic_rate=0.02,
        foreign_rate=0.01,
        time_to_maturity=0.25,
        option_type=OptionType.CALL,
    )

    put = call.model_copy(update={"option_type": OptionType.PUT})

    d1, d2 = BlackScholesFX.calculate_d1_d2(call)

    call_price = BlackScholesFX.price(call, d1, d2, 1.0)
    put_price = BlackScholesFX.price(put, d1, d2, 1.0)

    lhs = call_price + call.strike * np.exp(-call.domestic_rate * call.time_to_maturity)
    rhs = put_price + call.spot_price * np.exp(
        -call.foreign_rate * call.time_to_maturity
    )

    assert np.isclose(lhs, rhs), f"Parity failed: LHS {lhs} != RHS {rhs}"


def test_notional_conversion():
    """Test the notional conversion"""

    # Notional is in USD (Quote), Spot is 1.1 , 1,100,000 USD / 1.1 = 1,000,000 EUR
    call_usd = FXOption(
        id="T01_USD",
        underlying="EUR/USD",
        notional=1100000,
        notional_currency="USD",
        spot_price=1.1,
        strike=1.12,
        volatility=0.11,
        domestic_rate=0.02,
        foreign_rate=0.01,
        time_to_maturity=0.25,
        option_type=OptionType.CALL,
    )

    # Notional is already in EUR
    call_eur = call_usd.model_copy(
        update={"notional": 1000000, "notional_currency": "EUR"}
    )

    mult_quote = BlackScholesFX.get_notional(call_usd)
    mult_base = BlackScholesFX.get_notional(call_eur)

    assert math.isclose(
        mult_quote, 1000000.0
    ), f"USD conversion failed: got {mult_quote}"
    assert math.isclose(
        mult_base, 1000000.0
    ), f"Base currency should not be divided: got {mult_base}"


def test_at_maturity_intrinsic_value():
    """Ensures options at maturity return intrinsic value"""

    call_itm = FXOption(
        id="MATURITY_TEST",
        underlying="EUR/USD",
        spot_price=1.2,
        strike=1.1,
        volatility=0.1,
        domestic_rate=0.01,
        foreign_rate=0.01,
        time_to_maturity=0,
        notional=1,
        notional_currency="EUR",
        option_type=OptionType.CALL,
    )

    result = BlackScholesFX.calculate_greeks_and_pv(call_itm)

    assert math.isclose(result.pv, 0.1), f"PV should be 0.1, got {result.pv}"
    assert math.isclose(result.delta, 1.0), f"Delta should be 1.0, got {result.delta}"
    assert math.isclose(result.vega, 0.0), f"Vega should be 0.0, got {result.vega}"
