import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class DCFModel:
    """
    Discounted Cash Flow model for a Swiss Training & Consulting Company
    """
    
    def __init__(self):
        # Default input parameters
        self.base_revenue = 1_500_000  # CHF
        self.revenue_growth_rate = 0.12  # 12%
        self.terminal_growth_rate = 0.02  # 2%
        self.ebitda_margin = 0.25  # 25%
        self.tax_rate = 0.1379  # 13.79%
        self.depreciation_rate = 0.03  # 3% of revenue
        self.capex_rate = 0.01  # 1% of revenue
        self.wc_change_rate = 0.15  # 15% of revenue change
        self.discount_rate = 0.102  # 10.2%
        self.terminal_ebitda_multiple = 1.2  # 1.2x
        self.net_debt = 20_000 # CHF
        self.forecast_years = 5
        
        # Initialize dataframe for projections
        self.initialize_dataframe()
        
        # WACC components
        self.wacc_components = {
            'equity_weight': 0.70,  # 70%
            'debt_weight': 0.30,  # 30%
            'cost_of_equity': 0.10,  # 10%
            'pre_tax_cost_of_debt': 0.035,  # 3.5%
            'tax_rate': 0.18,  # 18%
            'business_risk_premium': 0.023  # 2.3%
        }
    
    def initialize_dataframe(self):
        """Initialize the projection dataframe with years"""
        years = ['Base'] + [f'Year {i+1}' for i in range(self.forecast_years)] + ['Terminal']
        self.projections = pd.DataFrame(index=years)
    
    def set_inputs(self, **kwargs):
        """Update model inputs with provided values"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Warning: {key} is not a valid input parameter")
        
        # Re-initialize dataframe when inputs change
        self.initialize_dataframe()
    
    def calculate_wacc(self):
        """Calculate WACC based on components"""
        w = self.wacc_components
        after_tax_cost_of_debt = w['pre_tax_cost_of_debt'] * (1 - w['tax_rate'])
        wacc = (w['equity_weight'] * w['cost_of_equity'] + 
                w['debt_weight'] * after_tax_cost_of_debt + 
                w['business_risk_premium'])
        return wacc
    
    def update_wacc_components(self, **kwargs):
        """Update WACC components"""
        for key, value in kwargs.items():
            if key in self.wacc_components:
                self.wacc_components[key] = value
            else:
                print(f"Warning: {key} is not a valid WACC component")
        
        # Update discount rate based on new WACC
        self.discount_rate = self.calculate_wacc()
    
    def project_revenue(self):
        """Project revenue for forecast period and terminal year"""
        # Base year
        self.projections.loc['Base', 'Revenue'] = self.base_revenue
        
        # Forecast years
        for i in range(1, self.forecast_years + 1):
            prev_year = 'Base' if i == 1 else f'Year {i-1}'
            current_year = f'Year {i}'
            self.projections.loc[current_year, 'Revenue'] = (
                self.projections.loc[prev_year, 'Revenue'] * (1 + self.revenue_growth_rate)
            )
        
        # Terminal year
        last_forecast_year = f'Year {self.forecast_years}'
        self.projections.loc['Terminal', 'Revenue'] = (
            self.projections.loc[last_forecast_year, 'Revenue'] * (1 + self.terminal_growth_rate)
        )
    
    def calculate_ebitda(self):
        """Calculate EBITDA based on revenue and margin"""
        for year in self.projections.index:
            if 'Revenue' in self.projections.columns:
                self.projections.loc[year, 'EBITDA'] = (
                    self.projections.loc[year, 'Revenue'] * self.ebitda_margin
                )
    
    def calculate_depreciation(self):
        """Calculate depreciation based on revenue"""
        for year in self.projections.index:
            if 'Revenue' in self.projections.columns:
                self.projections.loc[year, 'Depreciation'] = (
                    self.projections.loc[year, 'Revenue'] * self.depreciation_rate
                )
    
    def calculate_ebit(self):
        """Calculate EBIT (EBITDA - Depreciation)"""
        for year in self.projections.index:
            if 'EBITDA' in self.projections.columns and 'Depreciation' in self.projections.columns:
                self.projections.loc[year, 'EBIT'] = (
                    self.projections.loc[year, 'EBITDA'] - self.projections.loc[year, 'Depreciation']
                )
    
    def calculate_taxes(self):
        """Calculate taxes based on EBIT and tax rate"""
        for year in self.projections.index:
            if 'EBIT' in self.projections.columns:
                self.projections.loc[year, 'Taxes'] = (
                    self.projections.loc[year, 'EBIT'] * self.tax_rate
                )
    
    def calculate_nopat(self):
        """Calculate NOPAT (Net Operating Profit After Tax)"""
        for year in self.projections.index:
            if 'EBIT' in self.projections.columns and 'Taxes' in self.projections.columns:
                self.projections.loc[year, 'NOPAT'] = (
                    self.projections.loc[year, 'EBIT'] - self.projections.loc[year, 'Taxes']
                )
    
    def calculate_capex(self):
        """Calculate capital expenditures based on revenue"""
        for year in self.projections.index:
            if 'Revenue' in self.projections.columns:
                self.projections.loc[year, 'CAPEX'] = (
                    self.projections.loc[year, 'Revenue'] * self.capex_rate
                )
    
    def calculate_working_capital_change(self):
        """Calculate change in working capital based on revenue change"""
        self.projections.loc['Base', 'WC Change'] = 0
        
        for i in range(1, self.forecast_years + 1):
            prev_year = 'Base' if i == 1 else f'Year {i-1}'
            current_year = f'Year {i}'
            if 'Revenue' in self.projections.columns:
                revenue_change = (
                    self.projections.loc[current_year, 'Revenue'] - 
                    self.projections.loc[prev_year, 'Revenue']
                )
                self.projections.loc[current_year, 'WC Change'] = revenue_change * self.wc_change_rate
        
        # Terminal year
        last_forecast_year = f'Year {self.forecast_years}'
        if 'Revenue' in self.projections.columns:
            revenue_change = (
                self.projections.loc['Terminal', 'Revenue'] - 
                self.projections.loc[last_forecast_year, 'Revenue']
            )
            self.projections.loc['Terminal', 'WC Change'] = revenue_change * self.wc_change_rate
    
    def calculate_free_cash_flow(self):
        """Calculate free cash flow"""
        required_columns = ['NOPAT', 'Depreciation', 'CAPEX', 'WC Change']
        
        if all(col in self.projections.columns for col in required_columns):
            for year in self.projections.index:
                self.projections.loc[year, 'FCF'] = (
                    self.projections.loc[year, 'NOPAT'] +
                    self.projections.loc[year, 'Depreciation'] -
                    self.projections.loc[year, 'CAPEX'] -
                    self.projections.loc[year, 'WC Change']
                )
    
    def calculate_discount_factors(self):
        """Calculate discount factors for each year"""
        self.projections.loc['Base', 'Discount Factor'] = 1.0
        
        for i in range(1, self.forecast_years + 1):
            year = f'Year {i}'
            self.projections.loc[year, 'Discount Factor'] = 1 / ((1 + self.discount_rate) ** i)
        
        # Terminal year uses same discount factor as last forecast year
        self.projections.loc['Terminal', 'Discount Factor'] = self.projections.loc[f'Year {self.forecast_years}', 'Discount Factor']
    
    def calculate_present_values(self):
        """Calculate present values of cash flows"""
        if 'FCF' in self.projections.columns and 'Discount Factor' in self.projections.columns:
            for year in self.projections.index:
                if year != 'Terminal':  # Terminal value calculated separately
                    self.projections.loc[year, 'PV of FCF'] = (
                        self.projections.loc[year, 'FCF'] * self.projections.loc[year, 'Discount Factor']
                    )
    
    def calculate_terminal_value(self):
        """Calculate terminal value using perpetuity growth method and exit multiple method"""
        last_year = f'Year {self.forecast_years}'
        
        if 'FCF' in self.projections.columns and 'EBITDA' in self.projections.columns:
            # Perpetuity growth method
            terminal_fcf = self.projections.loc['Terminal', 'FCF']
            terminal_value_growth = terminal_fcf / (self.discount_rate - self.terminal_growth_rate)
            
            # Exit multiple method
            terminal_value_multiple = (
                self.projections.loc[last_year, 'EBITDA'] * self.terminal_ebitda_multiple
            )
            
            # Save to dataframe
            self.terminal_value_growth = terminal_value_growth
            self.terminal_value_multiple = terminal_value_multiple
            
            # Use perpetuity growth method as default
            self.terminal_value = terminal_value_growth
            
            # Calculate PV of terminal value
            self.pv_terminal_value = (
                self.terminal_value * self.projections.loc[last_year, 'Discount Factor']
            )
    
    def calculate_enterprise_value(self):
        """Calculate enterprise value"""
        if 'PV of FCF' in self.projections.columns:
            # Sum PV of explicit forecast period FCFs
            sum_pv_fcf = 0
            for i in range(1, self.forecast_years + 1):
                year = f'Year {i}'
                sum_pv_fcf += self.projections.loc[year, 'PV of FCF']
            
            self.enterprise_value = sum_pv_fcf + self.pv_terminal_value
    
    def calculate_equity_value(self):
        """Calculate equity value by subtracting net debt from enterprise value"""
        self.equity_value = self.enterprise_value - self.net_debt
    
    def run_dcf_model(self):
        """Run the complete DCF model calculation process"""
        self.project_revenue()
        self.calculate_ebitda()
        self.calculate_depreciation()
        self.calculate_ebit()
        self.calculate_taxes()
        self.calculate_nopat()
        self.calculate_capex()
        self.calculate_working_capital_change()
        self.calculate_free_cash_flow()
        self.calculate_discount_factors()
        self.calculate_present_values()
        self.calculate_terminal_value()
        self.calculate_enterprise_value()
        self.calculate_equity_value()
        
        return {
            'projections': self.projections,
            'enterprise_value': self.enterprise_value,
            'equity_value': self.equity_value,
            'terminal_value_growth': self.terminal_value_growth,
            'terminal_value_multiple': self.terminal_value_multiple
        }
    
    def sensitivity_analysis(self, wacc_range, growth_range):
        """
        Perform sensitivity analysis on WACC and terminal growth rate
        
        Parameters:
        wacc_range: List of WACC values to test
        growth_range: List of terminal growth rates to test
        
        Returns:
        DataFrame with sensitivity analysis results
        """
        # Store original values to restore after analysis
        original_wacc = self.discount_rate
        original_growth = self.terminal_growth_rate
        
        # Create empty DataFrame for results
        sensitivity = pd.DataFrame(index=wacc_range, columns=growth_range)
        
        # Perform analysis
        for wacc in wacc_range:
            for growth in growth_range:
                self.discount_rate = wacc
                self.terminal_growth_rate = growth
                self.run_dcf_model()
                sensitivity.loc[wacc, growth] = round(self.equity_value)
        
        # Restore original values
        self.discount_rate = original_wacc
        self.terminal_growth_rate = original_growth
        self.run_dcf_model()
        
        return sensitivity
    
    def plot_projections(self):
        """Plot key financial projections"""
        if not 'Revenue' in self.projections.columns:
            self.run_dcf_model()
        
        # Extract forecast years (excluding Base and Terminal)
        forecast_years = [year for year in self.projections.index if year != 'Base' and year != 'Terminal']
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Revenue and EBITDA
        ax1 = axes[0, 0]
        ax1.bar(forecast_years, self.projections.loc[forecast_years, 'Revenue'], alpha=0.7, label='Revenue')
        ax1.set_title('Revenue Projection')
        ax1.set_ylabel('CHF')
        ax1_twin = ax1.twinx()
        ax1_twin.plot(forecast_years, self.projections.loc[forecast_years, 'EBITDA'], 'ro-', label='EBITDA')
        ax1_twin.set_ylabel('EBITDA (CHF)', color='r')
        
        # Free Cash Flow
        ax2 = axes[0, 1]
        ax2.bar(forecast_years, self.projections.loc[forecast_years, 'FCF'], color='green', alpha=0.7)
        ax2.set_title('Free Cash Flow')
        ax2.set_ylabel('CHF')
        
        # EBIT and NOPAT
        ax3 = axes[1, 0]
        ax3.plot(forecast_years, self.projections.loc[forecast_years, 'EBIT'], 'bo-', label='EBIT')
        ax3.plot(forecast_years, self.projections.loc[forecast_years, 'NOPAT'], 'go-', label='NOPAT')
        ax3.set_title('EBIT and NOPAT')
        ax3.set_ylabel('CHF')
        ax3.legend()
        
        # Present Value of FCF
        ax4 = axes[1, 1]
        ax4.bar(forecast_years, self.projections.loc[forecast_years, 'PV of FCF'], color='purple', alpha=0.7)
        ax4.set_title('Present Value of Free Cash Flows')
        ax4.set_ylabel('CHF')
        
        plt.tight_layout()
        return fig
    
    def summary(self):
        """Print a summary of the DCF model results"""
        if not hasattr(self, 'equity_value'):
            self.run_dcf_model()
        
        print("=== DCF MODEL SUMMARY ===")
        print(f"Enterprise Value: CHF {self.enterprise_value:,.2f}")
        print(f"Equity Value: CHF {self.equity_value:,.2f}")
        print("\nTerminal Value:")
        print(f"  - Perpetuity Growth Method: CHF {self.terminal_value_growth:,.2f}")
        print(f"  - Exit Multiple Method: CHF {self.terminal_value_multiple:,.2f}")
        print(f"  - PV of Terminal Value: CHF {self.pv_terminal_value:,.2f}")
        print(f"  - % of Enterprise Value: {(self.pv_terminal_value / self.enterprise_value) * 100:.1f}%")
        
        print("\nKey Inputs:")
        print(f"  - Base Revenue: CHF {self.base_revenue:,.2f}")
        print(f"  - Revenue Growth Rate: {self.revenue_growth_rate:.1%}")
        print(f"  - Terminal Growth Rate: {self.terminal_growth_rate:.1%}")
        print(f"  - EBITDA Margin: {self.ebitda_margin:.1%}")
        print(f"  - Discount Rate (WACC): {self.discount_rate:.1%}")
        
        # Calculate implied valuation multiples
        last_year = f'Year {self.forecast_years}'
        ev_ebitda = self.enterprise_value / self.projections.loc[last_year, 'EBITDA']
        ev_revenue = self.enterprise_value / self.projections.loc[last_year, 'Revenue']
        
        print("\nImplied Valuation Multiples:")
        print(f"  - EV/EBITDA: {ev_ebitda:.2f}x")
        print(f"  - EV/Revenue: {ev_revenue:.2f}x")



if __name__ == "__main__":
    # Create a new DCF model with default parameters
    dcf = DCFModel()
    
    # Optionally update input parameters
    dcf.set_inputs(
   
    )
    
    # Run the DCF model
    results = dcf.run_dcf_model()
    
    # Print summary
    dcf.summary()
    
    # Perform sensitivity analysis
    wacc_range = [0.082, 0.092, 0.102, 0.112, 0.122]  # 8.2% to 12.2%
    growth_range = [-0.02, -0.01, 0.00, 0.01, 0.02]  # -2% to 2%
    sensitivity = dcf.sensitivity_analysis(wacc_range, growth_range)
    
    print("\n=== SENSITIVITY ANALYSIS (Equity Value in CHF) ===")
    print(sensitivity.round(0))
    
    # Generate and display plots
    fig = dcf.plot_projections()
    plt.show()