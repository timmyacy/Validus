# Uses BS Implementation for FXOptions (https://www.sciencedirect.com/science/article/abs/pii/S0261560683800011)
import numpy as np
import scipy.stats as stats
from src.models import FXOption, OptionType
from src.models import FXOptionResult
import logging

logger = logging.getLogger(__name__)

class BlackScholesFX:

    @staticmethod
    def calculate_d1_d2(option: FXOption):
        """
        Calculates the BS factors d1 and d2

        :param option: The option object containing market data
        :return: Tuple of d1 and d2
        """
        spot, strike = option.spot_price, option.strike
        time_to_maturity, volatility = option.time_to_maturity, option.volatility
        domestic_rate, foreign_rate = option.domestic_rate, option.foreign_rate

        # Implementation of the paper atop the file link

        d1 =  (np.log(spot/ strike) + (domestic_rate - foreign_rate +
            volatility**2/2) *time_to_maturity)/(volatility*np.sqrt(time_to_maturity))
        d2 = d1 - volatility * np.sqrt(time_to_maturity)
        return d1,d2

    @staticmethod
    def get_notional(option:FXOption):
        """
        Adjusts the notional amount based on the currency of the contract.

        :param option: The option object containing market data
        :return: The converted notional.
        """

        # Split the underlying currency into base and quote currency
        base_currency, quote_currency = option.underlying.split("/")
        if option.notional_currency == base_currency:
            return option.notional
        # If notional is in quote currency, it is converted to base currency using the current spot price.
        else:
            return option.notional/option.spot_price


    @staticmethod
    def price(option:FXOption,d1:float, d2:float,multiplier: float):

        """
        Calculate the present value of the option

        :param option: The FXOption object containing market data.
        :param d1: The first factor of the BS FXOption eqn.
        :param d2: The second factor of the BS FXOption eqn.
        :param multiplier: The notional multiplier
        :return: Total present value of the option scaled by notional
        """


        # Calculate the discount factors
        dr = np.exp(-option.domestic_rate*option.time_to_maturity)
        fr = np.exp(-option.foreign_rate*option.time_to_maturity)

        # Calculate the unit price accordingly for option type then scale by notional
        if option.option_type == OptionType.CALL:
            unit_pv = option.spot_price * fr * stats.norm.cdf(d1) - option.strike * dr * stats.norm.cdf(d2)
        else:
            unit_pv = option.strike * dr * stats.norm.cdf(-d2) - option.spot_price * fr * stats.norm.cdf(-d1)

        return unit_pv * multiplier

    @staticmethod
    def calculate_delta(option:FXOption,d1:float, multiplier: float):
        """
        Calculate the delta of the option

        :param option: The FXOption object containing market data.
        :param d1: The first factor of the BS FXOption eqn.
        :param multiplier: The notional multiplier
        :return: The delta of the FXOption scaled by notional, showing how much is needed to hedge the option
        """

        #  Discount by the foreign interest rate
        fr = np.exp(-option.foreign_rate*option.time_to_maturity)

        if option.option_type == OptionType.CALL:
            # Call Delta - e^(-foreign_rate * T) * N(d1)
            delta = fr * stats.norm.cdf(d1)

        else:
            # Put Delta = e ^ (-foreign_rate * T) * (N(d1) -1)
            delta = fr * (stats.norm.cdf(d1) -1)
        return delta * multiplier

    @staticmethod
    def calculate_vega(option:FXOption,d1:float, multiplier: float):
        """
        This calculates the sensitivity to the volatility of the underlying asset i.e. The vega of the FX option. .

        :param option: The FXOption object containing market data.
        :param d1: The first factor of the BS FXOption eqn.
        :param multiplier: The notional multiplier
        :return: Total Vega scaled by notional and reported per 1% change in vol.
        """

        fr = np.exp(-option.foreign_rate*option.time_to_maturity)

        # The factor of 0.01 is to convert the vega to percentage change in volatility
        vega = fr * option.spot_price * np.sqrt(option.time_to_maturity) * stats.norm.pdf(d1) * 0.01

        return vega * multiplier

    @staticmethod
    def calculate_greeks_and_pv(option:FXOption):
        """
        This collates all the greeks and pv for a given option
        :param option: The FXOption object containing market data.
        :return: FXOptionResult object containing the greeks and pv
        """
        # Handling options at or past maturity (T <= 0)
        if option.time_to_maturity <= 0:
            # At maturity, the option value is the intrinsic value
            if option.option_type == OptionType.CALL:
                value = max(option.spot_price - option.strike, 0)
                delta = 1 if option.spot_price > option.strike else 0
            else:
                value = max(option.strike - option.spot_price, 0)
                delta = -1 if option.strike > option.spot_price else 0
            multiplier = BlackScholesFX.get_notional(option)

            # Vega is always zero at maturity
            return FXOptionResult(id=option.id,pv=float(value * multiplier),delta=float(delta * multiplier),vega=0)
        else:
            d1, d2 = BlackScholesFX.calculate_d1_d2(option)
            multiplier = BlackScholesFX.get_notional(option)

            # Add debug level to show conversion of for each level
            logger.debug(
                f"Trade {option.id}: Notional converted from {option.notional_currency} to {option.underlying.split('/')[0]} using spot {option.spot_price}"
            )
            logger.debug(f"Trade {option.id}: d1 = {d1}, d2 = {d2}")
            # Calculate all greeks and pv for options as normal
            return FXOptionResult(
                id=option.id,
                pv=float(BlackScholesFX.price(option,d1,d2,multiplier)),
                delta=float(BlackScholesFX.calculate_delta(option,d1,multiplier)),
                vega=float(BlackScholesFX.calculate_vega(option,d1,multiplier))
            )



