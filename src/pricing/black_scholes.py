# Uses BS Implementation for FXOptions (https://www.sciencedirect.com/science/article/abs/pii/S0261560683800011)

from src.models.option import FXOption, OptionType
import numpy as np
from scipy.stats import norm

class BlackScholesFX:

    def __init__(self,option: FXOption):
        self.option = option


    def calculate_d1(self):
        spot, strike = self.option.spot_price, self.option.strike
        domestic_rate, foreign_rate = self.option.domestic_rate, self.option.foreign_rate
        volatility,time_to_maturity = self.option.volatility, self.option.time_to_maturity

        return (np.log(spot/strike) + (domestic_rate - foreign_rate+ volatility**2/2) *time_to_maturity)/(volatility*np.sqrt(time_to_maturity))


    def calculate_d2(self,d1):
        return d1 - self.option.volatility*np.sqrt(self.option.time_to_maturity)

    def price(self):
        d1 = self.calculate_d1()
        d2 = self.calculate_d2(d1)

        dr = np.exp(-self.option.domestic_rate*self.option.time_to_maturity)
        fr = np.exp(-self.option.foreign_rate*self.option.time_to_maturity)

        return self.option.spot_price * fr * norm.cdf(d1) -self.option.strike * dr * norm.cdf(d2)

    def calculate_greeks(self):
        pass


if __name__ == "__main__":
    test = FXOption(id="id001", option_type= OptionType.CALL,strike=1.12,spot_price=1.1,volatility=0.11,time_to_maturity=0.25,domestic_rate=0.01,foreign_rate=0.02)

    val = BlackScholesFX(test)
    print(f"Option Price: {val.price():.4f}")