import pandas as pd
from src.models import FXOption
import logging
from pydantic import ValidationError
logger = logging.getLogger(__name__)
class FileReader:
    @staticmethod
    def load_data(input_path: str):
        """
        Load in the .xlsx file and return a list of FXOption objects
        :param input_path: Path of the input .xlsx file

        :return: List of FXOption objects
        """

        # Read in file and map column names to model attributes

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

        # Convert rows to dictionaries and FXOption instances
        df = df.rename(columns=column_mapping)
        valid_trades = []

        # Iterate through each row and validate individually
        for record in df.to_dict('records'):
            try:
                # Instantiate the Pydantic model
                valid_trades.append(FXOption(**record))

            except ValidationError as e:
                # If validation fails, extract the exact error message and skip the trade
                error_msg = e.errors()
                logger.warning(f"Skipping invalid trade {record.get('id')}: {error_msg}")
        if not valid_trades:
            logger.warning("No valid trades found all  records failed validation.")
        return valid_trades
