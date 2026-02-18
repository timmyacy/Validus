# TODO: Reading Class
# Pass in excel data
import argparse

import pandas as pd
import sys
from src.models.option import FXOption
from src.models.result import PortfolioSummary
from src.pricing.black_scholes import BlackScholesFX


class FileReader:
    @staticmethod
    def load_data(input_path: str, output_path: str):

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

        results = []

        results_dict = df.to_dict('records')

        for record in results_dict:
            option = FXOption(**record)

            result = BlackScholesFX.calculate_greeks_and_pv(option)
            results.append(result)

        summary = PortfolioSummary(
            total_pv=sum(r.pv for r in results),
            total_delta=sum(r.delta for r in results),
            total_vega=sum(r.vega for r in results),
            num_of_trades=len(results)
        )

        results_df = pd.DataFrame([result.model_dump() for result in results])


        print(f"Calculation complete for {summary.num_of_trades} trades")
        summary_df = pd.DataFrame([summary.model_dump()])

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            results_df.to_excel(writer, sheet_name='Individual Greeks')
            summary_df.to_excel(writer, sheet_name='Portfolio Summary')
        print(f"Output saved to: {output_path}")




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FXOption Pricer")

    parser.add_argument("input", help="Path to the input .xlsx file")
    parser.add_argument("output", help="Path to the output .xlsx file")

    args = parser.parse_args()

    FileReader.load_data(args.input, args.output)