# Uses BS Implementation for FXOptions (https://www.sciencedirect.com/science/article/abs/pii/S0261560683800011)

from src.models.option import FXOption, OptionType
import numpy as np
from scipy.stats import norm

from src.models.result import FXOptionResult


class BlackScholesFX:

    @staticmethod
    def calculate_d1_d2(option: FXOption):
        spot, strike = option.spot_price, option.strike
        time_to_maturity, volatility = option.time_to_maturity, option.volatility
        domestic_rate, foreign_rate = option.domestic_rate, option.foreign_rate
        d1 =  (np.log(spot/ strike) + (domestic_rate - foreign_rate +
            volatility**2/2) *time_to_maturity)/(volatility*np.sqrt(time_to_maturity))
        d2 = d1 - volatility * np.sqrt(time_to_maturity)
        return d1,d2



    @staticmethod
    def get_notional(option:FXOption):
        base_currency, quote_currency = option.underlying.split("/")

        if option.notional_currency == base_currency:
            return option.notional
        else:
            return option.notional/option.spot_price


    @staticmethod
    def price(option:FXOption):
        d1,d2 = BlackScholesFX.calculate_d1_d2(option)

        dr = np.exp(-option.domestic_rate*option.time_to_maturity)

        fr = np.exp(-option.foreign_rate*option.time_to_maturity)

        multiplier = BlackScholesFX.get_notional(option)

        if option.option_type == OptionType.CALL:
            unit_pv = option.spot_price * fr * norm.cdf(d1) - option.strike * dr * norm.cdf(d2)
        else:
            unit_pv = option.strike * dr * norm.cdf(-d2) - option.spot_price * fr * norm.cdf(-d1)

        return unit_pv * multiplier

    @staticmethod
    def calculate_delta(option:FXOption):
        d1, _ = BlackScholesFX.calculate_d1_d2(option)
        fr = np.exp(-option.foreign_rate*option.time_to_maturity)
        multiplier = BlackScholesFX.get_notional(option)

        if option.option_type == OptionType.CALL:
            delta = fr * norm.cdf(d1)

        else:
            delta = fr * (norm.cdf(d1) -1)
        return delta * multiplier

    @staticmethod
    def calculate_vega(option:FXOption):
        d1, _ = BlackScholesFX.calculate_d1_d2(option)
        fr = np.exp(-option.foreign_rate*option.time_to_maturity)
        multiplier = BlackScholesFX.get_notional(option)
        vega = fr * option.spot_price * np.sqrt(option.time_to_maturity) * norm.pdf(d1) * 0.01

        return vega * multiplier

    @staticmethod
    def calculate_greeks_and_pv(option:FXOption):
        if option.time_to_maturity <= 0:
            if option.option_type == OptionType.CALL:
                value = max(option.spot_price - option.strike, 0)
                delta = 1 if option.spot_price > option.strike else 0
            else:
                value = max(option.strike - option.spot_price, 0)
                delta = -1 if option.strike > option.spot_price else 0
            multiplier = BlackScholesFX.get_notional(option)
            return FXOptionResult(id=option.id,pv=float(value * multiplier),delta=float(delta * multiplier),vega=0)
        else:
            return FXOptionResult(
                id=option.id,
                pv=float(BlackScholesFX.price(option)),
                delta=float(BlackScholesFX.calculate_delta(option)),
                vega=float(BlackScholesFX.calculate_vega(option))
            )


if __name__ == "__main__":
    test = FXOption(id="id001", option_type= OptionType.CALL,strike=1.12,spot_price=1.1,volatility=0.11,time_to_maturity=0.25,domestic_rate=0.01,foreign_rate=0.02,underlying='EUR/USD',notional=1000000,notional_currency="USD")


    print(f"Option Price: {BlackScholesFX.price(test):.4f}\n")
    print(f"Greeks: {BlackScholesFX.calculate_greeks_and_pv(test)}")

