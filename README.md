### FX Options Portfolio Risk Aggregator

 This tool will price and aggregrate a portfolio of FX options

## Components

* Models: Greeks and data validation
    - Add Class for FX Option and Result (DONE)
* Pricing : Logic and Calculation of Greeks
    - Pricing Logic 
* I/O - File Handling i.e Reading and Writing 
    - Add REader for reading Excel files
    - Add Writer 
* Orchestration - Full pipeline herein

## Flow

```mermaid
graph LR
    A[Excel File] --> B[Load & Validate]
    B --> C[Price Options]
    C --> D[Calculate Greeks]
    D --> E[Aggregate Totals]
    E --> F[Export Results]
```
## Assumptions
* Standard Black-Scholes assumptions i.e constant Volatility, No dividends etc.

## Setup(WIP):
Dependencies - Can include requirements.txt