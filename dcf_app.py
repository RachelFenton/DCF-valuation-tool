import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from DCF_model import DCFModel

st.set_page_config(page_title="DCF Model for Swiss Company", layout="wide")

st.title("DCF Valuation Tool for Swiss Company")
st.write("Enter your company parameters below to calculate valuation.")

# Create tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["Basic Inputs", "Advanced Parameters", "Results", "Sensitivity Analysis"])

# Initialize the DCF model
@st.cache_resource
def get_dcf_model():
    return DCFModel()

dcf = get_dcf_model()

# Basic Inputs Tab
with tab1:
    st.header("Company Basics")

    col1, col2 = st.columns(2)

    with col1:
        base_revenue = st.number_input(
            "Base Year Revenue (CHF)",
            min_value=100000,
            max_value=100000000,
            value=1000000,
            step=100000,
            format="%d"
        )

        revenue_growth = st.slider(
            "Revenue Growth Rate (Years 1-5)",
            min_value=0.0,
            max_value=0.30,
            value=0.12,
            step=0.01,
            format="%.2f"
        )

        ebitda_margin = st.slider(
            "EBITDA Margin",
            min_value=0.05,
            max_value=0.50,
            value=0.25,
            step=0.01,
            format="%.2f"
        )

    with col2:
        terminal_growth = st.slider(
            "Terminal Growth Rate",
            min_value=0.01,
            max_value=0.05,
            value=0.02,
            step=0.005,
            format="%.3f"
        )

        discount_rate = st.slider(
            "Discount Rate (WACC)",
            min_value=0.06,
            max_value=0.15,
            value=0.102,
            step=0.002,
            format="%.3f"
        )

        net_debt = st.number_input(
            "Net Debt (CHF)",
            min_value=0,
            max_value=10000000,
            value=200000,
            step=50000,
            format="%d"
        )

# Advanced Parameters Tab
with tab2:
    st.header("Advanced DCF Parameters")

    col1, col2 = st.columns(2)

    with col1:
        tax_rate = st.slider(
            "Tax Rate",
            min_value=0.10,
            max_value=0.30,
            value=0.18,
            step=0.01,
            format="%.2f"
        )

        depreciation_rate = st.slider(
            "Depreciation (% of Revenue)",
            min_value=0.01,
            max_value=0.10,
            value=0.03,
            step=0.005,
            format="%.3f"
        )

        capex_rate = st.slider(
            "Capital Expenditure (% of Revenue)",
            min_value=0.01,
            max_value=0.10,
            value=0.04,
            step=0.005,
            format="%.3f"
        )

    with col2:
        wc_change_rate = st.slider(
            "Working Capital Change (% of Revenue Change)",
            min_value=0.05,
            max_value=0.30,
            value=0.15,
            step=0.01,
            format="%.2f"
        )

        terminal_multiple = st.slider(
            "Terminal EBITDA Multiple",
            min_value=4,
            max_value=15,
            value=8,
            step=1
        )

        forecast_years = st.slider(
            "Forecast Period (Years)",
            min_value=3,
            max_value=10,
            value=5,
            step=1
        )

    st.header("WACC Components")

    col1, col2 = st.columns(2)

    with col1:
        equity_weight = st.slider(
            "Equity Weight",
            min_value=0.40,
            max_value=1.0,
            value=0.70,
            step=0.05,
            format="%.2f"
        )

        cost_of_equity = st.slider(
            "Cost of Equity",
            min_value=0.06,
            max_value=0.20,
            value=0.10,
            step=0.01,
            format="%.2f"
        )

    with col2:
        debt_weight = 1 - equity_weight
        st.metric("Debt Weight", f"{debt_weight:.2f}")

        pre_tax_cost_of_debt = st.slider(
            "Pre-tax Cost of Debt",
            min_value=0.01,
            max_value=0.10,
            value=0.035,
            step=0.005,
            format="%.3f"
        )

        business_risk_premium = st.slider(
            "Business Risk Premium",
            min_value=0.0,
            max_value=0.05,
            value=0.023,
            step=0.002,
            format="%.3f"
        )

    # Calculate WACC
    after_tax_cost_of_debt = pre_tax_cost_of_debt * (1 - tax_rate)
    calculated_wacc = round((equity_weight * cost_of_equity) + (debt_weight * after_tax_cost_of_debt) + business_risk_premium, 4)

    st.info(f"Calculated WACC: {calculated_wacc:.2%}")

    use_calculated_wacc = st.checkbox("Use calculated WACC instead of manual input", value=False)
    if use_calculated_wacc:
        discount_rate = calculated_wacc

# Run the model when the user clicks the button
if st.button("Run DCF Model", type="primary"):
    # Update model parameters
    dcf.set_inputs(
        base_revenue=base_revenue,
        revenue_growth_rate=revenue_growth,
        terminal_growth_rate=terminal_growth,
        ebitda_margin=ebitda_margin,
        tax_rate=tax_rate,
        depreciation_rate=depreciation_rate,
        capex_rate=capex_rate,
        wc_change_rate=wc_change_rate,
        discount_rate=discount_rate if not use_calculated_wacc else calculated_wacc,
        terminal_ebitda_multiple=terminal_multiple,
        net_debt=net_debt,
        forecast_years=forecast_years
    )

    # Update WACC components if needed
    if use_calculated_wacc:
        dcf.update_wacc_components(
            equity_weight=equity_weight,
            debt_weight=debt_weight,
            cost_of_equity=cost_of_equity,
            pre_tax_cost_of_debt=pre_tax_cost_of_debt,
            tax_rate=tax_rate,
            business_risk_premium=business_risk_premium
        )

    # Run the model
    results = dcf.run_dcf_model()

    # Results Tab
    with tab3:
        st.header("DCF Valuation Results")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Enterprise Value", f"CHF {dcf.enterprise_value:,.0f}")
            st.metric("Equity Value", f"CHF {dcf.equity_value:,.0f}")

            # Calculate implied multiples
            last_year = f'Year {dcf.forecast_years}'
            ev_ebitda = dcf.enterprise_value / dcf.projections.loc[last_year, 'EBITDA']
            ev_revenue = dcf.enterprise_value / dcf.projections.loc[last_year, 'Revenue']

            st.metric("Implied EV/EBITDA", f"{ev_ebitda:.2f}x")
            st.metric("Implied EV/Revenue", f"{ev_revenue:.2f}x")

        with col2:
            # Terminal value breakdown
            st.subheader("Terminal Value Analysis")
            st.metric("Terminal Value (Perpetuity Growth)", f"CHF {dcf.terminal_value_growth:,.0f}")
            st.metric("Terminal Value (Exit Multiple)", f"CHF {dcf.terminal_value_multiple:,.0f}")
            tv_percentage = (dcf.pv_terminal_value / dcf.enterprise_value) * 100
            st.metric("Terminal Value % of EV", f"{tv_percentage:.1f}%")

        st.subheader("Detailed Projections")
        # Format the dataframe for display
        display_df = dcf.projections.copy()
        # Format currency columns
        for col in display_df.columns:
            if col != 'Discount Factor':
                display_df[col] = display_df[col].apply(lambda x: f"CHF {x:,.0f}" if not pd.isna(x) else "")
            else:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.4f}" if not pd.isna(x) else "")

        st.dataframe(display_df, use_container_width=True)

        # Create plots
        st.subheader("Visualization")
        fig = dcf.plot_projections()
        st.pyplot(fig)

    # Sensitivity Analysis Tab
    with tab4:
        st.header("Sensitivity Analysis")

        # Create WACC range based on current value
        base_wacc = discount_rate if not use_calculated_wacc else calculated_wacc
        wacc_range = [round(base_wacc - 0.02, 3), round(base_wacc - 0.01, 3),
                      round(base_wacc, 3),
                      round(base_wacc + 0.01, 3), round(base_wacc + 0.02, 3)]

        # Create growth range based on current value
        growth_range = [round(terminal_growth - 0.01, 3), round(terminal_growth - 0.005, 3),
                        round(terminal_growth, 3),
                        round(terminal_growth + 0.005, 3), round(terminal_growth + 0.01, 3)]

        # Run sensitivity analysis
        sensitivity = dcf.sensitivity_analysis(wacc_range, growth_range)

        # Format the sensitivity table
        sensitivity_formatted = sensitivity.copy()

        # Format to CHF thousands
        for col in sensitivity_formatted.columns:
            sensitivity_formatted[col] = sensitivity_formatted[col].apply(lambda x: f"CHF {x/1000:,.0f}k")

        st.write("Equity Value (CHF) Sensitivity to WACC and Terminal Growth Rate")
        st.dataframe(sensitivity_formatted, use_container_width=True)

        # Create a heatmap of the sensitivity analysis
        #st.subheader("Sensitivity Heatmap")

        # Plot heatmap
        #fig, ax = plt.subplots(figsize=(10, 6))

        # Convert sensitivity data for heatmap
       # sensitivity_data = sensitivity.to_numpy()

        #im = ax.imshow(sensitivity_data, cmap="YlGn")

        # Add colorbar
        #cbar = ax.figure.colorbar(im, ax=ax)
        #cbar.ax.set_ylabel("Equity Value (CHF)", rotation=-90, va="bottom")

        # Show all ticks and label them
        #ax.set_xticks(np.arange(len(growth_range)))
        #ax.set_yticks(np.arange(len(wacc_range)))
        #ax.set_xticklabels([f"{x:.1%}" for x in growth_range])
        #ax.set_yticklabels([f"{x:.1%}" for x in wacc_range])

        # Label axes
        #ax.set_xlabel("Terminal Growth Rate")
        #ax.set_ylabel("WACC")
        #ax.set_title("DCF Sensitivity Analysis")

        # Add text annotations to the heatmap
        #for i in range(len(wacc_range)):
         #   for j in range(len(growth_range)):
          #      text = ax.text(j, i, f"{sensitivity_data[i, j]/1000000:.1f}M",
           #                   ha="center", va="center", color="black")

        #plt.tight_layout()
        #st.pyplot(fig)

#else:
    # Default message when app first loads
 #   with tab3:
  #      st.info("Enter your parameters and click 'Run DCF Model' to see results.")

#    with tab4:
 #       st.info("Enter your parameters and click 'Run DCF Model' to see sensitivity analysis.")

# Add helper information at the bottom
st.markdown("---")
st.markdown("""
### How to Use This Tool

1. **Basic Inputs**: Enter the fundamental financial parameters for your company
2. **Advanced Parameters**: Fine-tune the DCF model with detailed assumptions and WACC components
3. **Results**: View the calculated enterprise and equity values, along with detailed projections
4. **Sensitivity Analysis**: Explore how changes in WACC and terminal growth affect valuation

This app requires the `dcf_model.py` file to be in the same directory.
""")
