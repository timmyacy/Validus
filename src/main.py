import argparse
from src.io.reader import FileReader
from src.io.writer import FileWriter
from src.pricing.black_scholes import BlackScholesFX
from src.models.result import PortfolioSummary
import logging



def main():

    # Set up command line arguments
    parser = argparse.ArgumentParser(description="FXOption Pricer")

    parser.add_argument("input", help="Path to the input .xlsx file")
    parser.add_argument("output", help="Path to the output .xlsx file")
    parser.add_argument("--verbose",action="store_true",  help="Enable verbose logging")

    # Parse arguments
    args = parser.parse_args()

    # Setup default logging level
    log_level = logging.DEBUG if args.verbose else logging.INFO

    # Apply logging configuration
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")
    logger = logging.getLogger(__name__)


    logger.info("Loading data from .xlsx file")
    data = FileReader.load_data(args.input)

    logger.info("Calculating greeks and PVs for each trade")
    results = [BlackScholesFX.calculate_greeks_and_pv(t) for t in data]

    logger.info("Calculating total parameters for portfolio summary")
    summary = PortfolioSummary(
        total_pv=sum(r.pv for r in results),
        total_delta=sum(r.delta for r in results),
        total_vega=sum(r.vega for r in results),
        num_of_trades=len(results)
    )

    logger.info("Writing results to .xlsx file")
    FileWriter.write_data(results, summary, args.output)

    logger.info("Finished processing data")
    logger.info(f"Successfully processed {len(data)} trades.")

if __name__ == "__main__":
    main()