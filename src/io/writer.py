import pandas as pd
from src.models import FXOptionResult, PortfolioSummary


class FileWriter:
    @staticmethod
    def write_data(
        results: list[FXOptionResult], summary: PortfolioSummary, output_path: str
    ):
        """
        Export calculated greeks and totals to a multi-sheet Excel file

        :param results: List of result for each trade
        :param summary: Total values for the portfolio i.e total pv,total vega etc
        :param output_path: File path for generated .xlsx file

        """

        results_df = pd.DataFrame([r.model_dump() for r in results])
        summary_df = pd.DataFrame([summary.model_dump()])

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            results_df.to_excel(writer, sheet_name="Individual Greeks", index=False)
            summary_df.to_excel(writer, sheet_name="Portfolio Summary", index=False)
