import pandas as pd
from src.models.option import FXOption


class FileReader:
    @staticmethod
    def load_data(input_path: str):
        """

        :param input_path: Path of the input .xlsx file
        :return:
        """
        df = pd.read_excel(input_path)

        column_mapping = {
        "TradeID":"id",
        "Underlying": "underlying",
        "Notional":"notional",
        "NotionalCurrency": "notional_currency",
        "Spot": "spot_price",
        "Strike":"strike",
        "Vol":"volatility",
        "RateDomestic":"domestic_rate",
        "RateForeign": "foreign_rate",
        "Expiry":"time_to_maturity",
        "OptionType": "option_type"
        }

        df = df.rename(columns=column_mapping)
        return [FXOption(**record) for record in df.to_dict('records')]
