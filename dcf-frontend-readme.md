# DCF Valuation Tool for Swiss Training & Consulting Companies

This is a web-based frontend for the DCF (Discounted Cash Flow) model, built with Streamlit.

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Save the Python files**
   - Save the DCF model (`dcf_model.py`) and the Streamlit app (`dcf_app.py`) in the same folder
   - Save the requirements file (`requirements.txt`) in the same folder

2. **Create a virtual environment (recommended)**
   ```bash
   # Navigate to your project folder
   cd path/to/your/folder
   
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On Mac/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install the required packages**
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

1. **Start the Streamlit server**
   ```bash
   streamlit run dcf_app.py
   ```

2. **Access the app**
   - The app will automatically open in your default web browser
   - If it doesn't open automatically, you can access it at http://localhost:8501

## Using the DCF Tool

1. **Basic Inputs Tab**
   - Enter your company's base revenue
   - Set the growth rate, EBITDA margin, and other key parameters
   - Adjust the discount rate (WACC) and terminal growth rate

2. **Advanced Parameters Tab**
   - Fine-tune the DCF model with detailed assumptions
   - Customize WACC components for a more accurate discount rate
   - Adjust tax rates, depreciation, and capital expenditure assumptions

3. **Results Tab**
   - View the calculated enterprise and equity values
   - See detailed projections for all financial metrics
   - Explore graphical visualizations of key performance indicators

4. **Sensitivity Analysis Tab**
   - Understand how changes in WACC and terminal growth affect valuation
   - View the sensitivity matrix and heatmap visualization

## Customization

You can customize the app by:
- Modifying the ranges of sliders in `dcf_app.py`
- Adding additional inputs or visualizations
- Connecting to external data sources
- Exporting results to CSV or Excel

## Troubleshooting

If you encounter any issues:
- Make sure both Python files are in the same directory
- Verify that all required packages are installed
- Check that you're using a compatible Python version
- Ensure your terminal/command prompt is running from the correct directory
