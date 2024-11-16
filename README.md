# Bond Pricing Calculator

An advanced bond pricing calculator built with Python and Streamlit that helps analyze bond prices, yields, and risk metrics.


[Try it out here!](https://bond-price.streamlit.app/)

## Features

- Bond price calculation with different payment frequencies (Annual, Semi-annual, Quarterly, Monthly)
- Yield to Maturity (YTM) calculation
- Duration and Convexity analysis
- Price sensitivity calculator
- Interactive price-yield curve visualization
- Cash flow analysis and visualization
- Clean and dirty price calculations
- Accrued interest computation

## Installation

```bash
# Clone the repository
git clone https://github.com/upspal/Bond-pricer.git

# Navigate to the project directory
cd Bond-pricer

# Install required packages
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:
```bash
streamlit run bond_pricer.py
```

## Requirements

Create a requirements.txt file with all necessary dependencies:
```
streamlit
numpy
pandas
plotly
```