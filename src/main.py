import argparse
from src.io.reader import FileReader
from src.io.writer import FileWriter
from src.pricing.black_scholes import BlackScholesFX
from src.models.result import PortfolioSummary

def main():

    parser = argparse.ArgumentParser(description="FXOption Pricer")

    parser.add_argument("input", help="Path to the input .xlsx file")
    parser.add_argument("output", help="Path to the output .xlsx file")
    args = parser.parse_args()

    data = FileReader.load_data(args.input)

    results = [BlackScholesFX.calculate_greeks_and_pv(t) for t in data]

    summary = PortfolioSummary(
        total_pv=sum(r.pv for r in results),
        total_delta=sum(r.delta for r in results),
        total_vega=sum(r.vega for r in results),
        num_of_trades=len(results)
    )

    FileWriter.write_data(results, summary, args.output)
    print(f"Successfully processed {len(data)} trades.")

if __name__ == "__main__":
    main()