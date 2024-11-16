import numpy as np
import pandas as pd
import streamlit as st
from datetime import date
import plotly.graph_objects as go

def get_payments_per_year(frequency):
    """Convert payment frequency to number of payments per year"""
    frequency_map = {
        "Annual": 1,
        "Semi-annual": 2,
        "Quarterly": 4,
        "Monthly": 12
    }
    return frequency_map[frequency]

def adjust_rates_for_frequency(rate, frequency):
    """Adjust annual rates for payment frequency"""
    payments_per_year = get_payments_per_year(frequency)
    return rate / payments_per_year

def bond_pricer(face_value, coupon_rate, years_to_maturity, discount_rate, frequency="Annual"):
    """
    Calculate bond price with different payment frequencies
    """
    payments_per_year = get_payments_per_year(frequency)
    periods = int(years_to_maturity * payments_per_year)
    
    # Adjust rates for payment frequency
    periodic_coupon_rate = adjust_rates_for_frequency(coupon_rate, frequency)
    periodic_discount_rate = adjust_rates_for_frequency(discount_rate, frequency)
    
    coupon_payment = face_value * periodic_coupon_rate
    bond_price = 0
    
    for i in range(1, periods + 1):
        bond_price += coupon_payment / ((1 + periodic_discount_rate) ** i)
    bond_price += face_value / ((1 + periodic_discount_rate) ** periods)
    
    return bond_price

def calculate_yield_to_maturity(face_value, coupon_rate, years_to_maturity, price, frequency="Annual"):
    """Calculate yield to maturity using numerical method with payment frequency"""
    payments_per_year = get_payments_per_year(frequency)
    periods = int(years_to_maturity * payments_per_year)
    periodic_coupon_rate = adjust_rates_for_frequency(coupon_rate, frequency)
    
    def npv(ytm):
        periodic_ytm = ytm / payments_per_year
        total = -price
        coupon_payment = face_value * periodic_coupon_rate
        for i in range(1, periods + 1):
            total += coupon_payment / ((1 + periodic_ytm) ** i)
        total += face_value / ((1 + periodic_ytm) ** periods)
        return total

    # Use binary search to find YTM
    low, high = 0.0, 1.0
    for _ in range(50):
        mid = (low + high) / 2
        if npv(mid) > 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2

def calculate_duration(face_value, coupon_rate, years_to_maturity, discount_rate, frequency="Annual"):
    """Calculate Macaulay and Modified Duration with payment frequency"""
    payments_per_year = get_payments_per_year(frequency)
    periods = int(years_to_maturity * payments_per_year)
    
    periodic_coupon_rate = adjust_rates_for_frequency(coupon_rate, frequency)
    periodic_discount_rate = adjust_rates_for_frequency(discount_rate, frequency)
    
    coupon_payment = face_value * periodic_coupon_rate
    weighted_time = 0
    pv_total = 0
    
    for i in range(1, periods + 1):
        pv = coupon_payment / ((1 + periodic_discount_rate) ** i)
        weighted_time += (i / payments_per_year) * pv
        pv_total += pv
    
    final_pv = face_value / ((1 + periodic_discount_rate) ** periods)
    weighted_time += years_to_maturity * final_pv
    pv_total += final_pv
    
    macaulay_duration = weighted_time / pv_total
    modified_duration = macaulay_duration / (1 + periodic_discount_rate)
    
    return macaulay_duration, modified_duration

def calculate_convexity(face_value, coupon_rate, years_to_maturity, discount_rate, frequency="Annual"):
    """Calculate bond convexity with payment frequency"""
    payments_per_year = get_payments_per_year(frequency)
    periods = int(years_to_maturity * payments_per_year)
    
    periodic_coupon_rate = adjust_rates_for_frequency(coupon_rate, frequency)
    periodic_discount_rate = adjust_rates_for_frequency(discount_rate, frequency)
    
    coupon_payment = face_value * periodic_coupon_rate
    weighted_squares = 0
    pv_total = 0
    
    for i in range(1, periods + 1):
        period_in_years = i / payments_per_year
        pv = coupon_payment / ((1 + periodic_discount_rate) ** i)
        weighted_squares += period_in_years * (period_in_years + 1/payments_per_year) * pv
        pv_total += pv
    
    final_pv = face_value / ((1 + periodic_discount_rate) ** periods)
    weighted_squares += years_to_maturity * (years_to_maturity + 1/payments_per_year) * final_pv
    pv_total += final_pv
    
    convexity = weighted_squares / (pv_total * (1 + periodic_discount_rate) ** 2)
    return convexity

def calculate_accrued_interest(face_value, coupon_rate, last_payment_date, frequency="Annual"):
    """Calculate accrued interest since last payment"""
    payments_per_year = get_payments_per_year(frequency)
    days_per_period = 360 / payments_per_year  # Using 360-day year convention
    
    today = date.today()
    days_since_last_payment = (today - last_payment_date).days
    
    periodic_coupon_rate = adjust_rates_for_frequency(coupon_rate, frequency)
    accrued_interest = (days_since_last_payment / days_per_period) * (face_value * periodic_coupon_rate)
    
    return accrued_interest

def plot_yield_curve(bond_price, face_value, coupon_rate, years_to_maturity, frequency):
    """Plot the relationship between yield and price"""
    yields = np.linspace(0.01, 0.15, 100)
    prices = [bond_pricer(face_value, coupon_rate, years_to_maturity, y, frequency) for y in yields]
    return yields, prices

def create_cashflow_diagram(face_value, coupon_rate, years_to_maturity, frequency):
    """Create a cash flow diagram"""
    payments_per_year = get_payments_per_year(frequency)
    periods = int(years_to_maturity * payments_per_year)
    periodic_coupon_payment = face_value * (coupon_rate / payments_per_year)
    
    cashflows = [periodic_coupon_payment] * periods
    cashflows[-1] += face_value  # Add face value to final payment
    
    fig = go.Figure()
    
    # Add coupon payments
    payment_dates = [f"Year {i/payments_per_year:.2f}" for i in range(1, periods + 1)]
    
    fig.add_trace(go.Bar(
        x=payment_dates,
        y=cashflows,
        name="Cash Flows"
    ))
    
    fig.update_layout(
        title="Bond Cash Flow Diagram",
        xaxis_title="Payment Date",
        yaxis_title="Cash Flow ($)",
        height=300
    )
    
    return fig

def main():
    st.set_page_config(page_title="Advanced Bond Pricing Calculator", page_icon="💵", layout="wide")

    st.title("Advanced Bond Pricing Calculator")

    # Input Parameters
    with st.sidebar:
        st.title("Bond Pricing Calculator")
        st.write("Created by")
        linkedin = "https://www.linkedin.com/in/pranavuppall"
        github = "https://github.com/upspal"
        st.markdown(f'<a href="{linkedin}" target="_blank" style="text-decoration: none; color: inherit;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25" style="vertical-align: middle; margin-right: 10px;"></a><a href="{github}" target="_blank" style="text-decoration: none; color: inherit;"><img src="https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/github-white-icon.png" width="25" height="25" style="vertical-align: middle; margin-right: 10px;">`Pranav Uppal`</a>', unsafe_allow_html=True)
        st.subheader("Bond Parameters")
        face_value = st.number_input("Face Value ($)", min_value=100, step=100, value=1000)
        coupon_rate = st.slider("Coupon Rate (%)", min_value=0.0, max_value=50.0, value=5.0, step=0.1) / 100
        years_to_maturity = st.slider("Years to Maturity", min_value=1, max_value=100, step=1, value=10)
        discount_rate = st.slider("Discount Rate (%)", min_value=0.0, max_value=30.0, value=5.0, step=0.1) / 100
        
        payment_frequency = st.selectbox(
            "Payment Frequency", 
            ["Annual", "Semi-annual", "Quarterly", "Monthly"],
            index=1
        )
        
        last_payment_date = st.date_input(
            "Last Payment Date",
            value=date.today(),
            min_value=date.today(),
            max_value=date(2200, 12, 31)
        )

    # Main content
    tab1, tab2, tab3 = st.tabs(["Price Analysis", "Risk Metrics", "Cash Flows"])

    # Calculate key metrics
    bond_price = round(bond_pricer(face_value, coupon_rate, years_to_maturity, discount_rate, payment_frequency), 2)
    ytm = calculate_yield_to_maturity(face_value, coupon_rate, years_to_maturity, bond_price, payment_frequency)
    macaulay_duration, modified_duration = calculate_duration(face_value, coupon_rate, years_to_maturity, discount_rate, payment_frequency)
    convexity = calculate_convexity(face_value, coupon_rate, years_to_maturity, discount_rate, payment_frequency)
    accrued_interest = calculate_accrued_interest(face_value, coupon_rate, last_payment_date, payment_frequency)

    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Clean Price ($)", f"{bond_price:,.2f}")
            st.metric("Accrued Interest ($)", f"{accrued_interest:.2f}")
        with col2:
            st.metric("Dirty Price ($)", f"{bond_price + accrued_interest:,.2f}")
            st.metric("Yield to Maturity (%)", f"{ytm*100:.2f}")
        with col3:
            st.metric("Current Yield (%)", f"{(coupon_rate * face_value / bond_price)*100:.2f}")
            payments_per_year = get_payments_per_year(payment_frequency)
            st.metric("Periodic Payment ($)", f"{(face_value * coupon_rate / payments_per_year):,.2f}")

        # Price-Yield curve
        yields, prices = plot_yield_curve(bond_price, face_value, coupon_rate, years_to_maturity, payment_frequency)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=yields*100, y=prices, mode='lines', name='Price-Yield Relationship'))
        fig.add_trace(go.Scatter(x=[discount_rate*100], y=[bond_price], 
                               mode='markers', name='Current Position',
                               marker=dict(size=10, color='red')))
        
        fig.update_layout(
            title="Bond Price vs Yield",
            xaxis_title="Yield (%)",
            yaxis_title="Price ($)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Duration and Convexity Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Macaulay Duration (years)", f"{macaulay_duration:.2f}")
            st.metric("Modified Duration", f"{modified_duration:.2f}")
        with col2:
            st.metric("Convexity", f"{convexity:.2f}")
        
        # Price sensitivity calculator
        st.subheader("Price Sensitivity Calculator")
        yield_change = st.slider("Yield Change (basis points)", -100, 100, 0) / 10000
        
        duration_effect = -modified_duration * yield_change
        convexity_effect = 0.5 * convexity * yield_change**2
        total_effect = duration_effect + convexity_effect
        
        new_price = bond_price * (1 + total_effect)
        
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Price Change ($)", f"{new_price - bond_price:.2f}")
            st.metric("Percentage Change", f"{total_effect*100:.2f}%")
        with col4:
            st.metric("Duration Effect", f"{duration_effect*100:.2f}%")
            st.metric("Convexity Effect", f"{convexity_effect*100:.2f}%")

    with tab3:
        st.subheader("Cash Flow Analysis")
        cashflow_fig = create_cashflow_diagram(face_value, coupon_rate, years_to_maturity, payment_frequency)
        st.plotly_chart(cashflow_fig, use_container_width=True)

    # Footer with bond information
    st.markdown("---")
    payments_per_year = get_payments_per_year(payment_frequency)
    periodic_payment = face_value * coupon_rate / payments_per_year
    
    st.markdown(f"""
    **Bond Summary:**
    - Face Value: ${face_value:,.2f}
    - Annual Coupon Rate: {coupon_rate*100:.1f}%
    - Payment Frequency: {payment_frequency} ({payments_per_year} payments per year)
    - Payment Amount: ${periodic_payment:,.2f} per period
    - Time to Maturity: {years_to_maturity} years
    - Total Number of Payments: {int(years_to_maturity * payments_per_year)}
    """)

if __name__ == "__main__":
    main()