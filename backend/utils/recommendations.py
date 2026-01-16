from schemas import CustomerRecord

def _generate_recommendation(customer: CustomerRecord) -> str:
    """
    Generate recommendation text based on customer segment and churn risk.
    
    Args:
        customer: CustomerRecord with all customer data
    
    Returns:
        Text recommendation string
    """
    segment = customer.segment
    churn_label = customer.churn_label
    frequency_last_year = customer.frequency
    annual_value = customer.monetary
    days_since_last_purchase = customer.recency
    
    ## Recommendations currently static, but would incorporate language model endpoint to adapt/personalize to customer data points if time
    
    if segment == "Monthly, High-Value Buyers":
        return f"""
        - Reward consistency and loyalty
        This customer purchased {frequency_last_year} times in the past year and generates ${annual_value} annually. Introduce tiered rewards, priority access to new products, or volume-based incentives to reinforce their regular buying behavior.

        - Encourage larger or more strategic orders
        With their last purchase occurring {days_since_last_purchase} days ago, prompt reorders using bulk discounts, personalized reorder reminders, or exclusive bundles aligned to their purchase history.

        - Protect against churn despite high value
        Even high-performing customers can lapse. Assign a dedicated account touchpoint or proactive outreach if recency exceeds expected monthly cadence to preserve long-term value."""
    
    elif segment == "Seasonal Buyers":
        return f"""
        - Time outreach around known buying cycles
        This customer last purchased {days_since_last_purchase} days ago, indicating a seasonal pattern. Use historical purchase timing to trigger campaigns just before their typical buying window.

        - Increase value during active periods
        With {frequency_last_year} purchases and ${annual_value} annual spend, focus on maximizing order size during peak seasons through bundles, add-ons, or limited-time promotions.

        - Maintain light engagement off-season
        Avoid over-marketing during inactive periods. Instead, use low-touch content (new arrivals, planning tools, early previews) to stay top-of-mind without driving fatigue."""
    
    else:  # Experimental / Hesitant, Lower-Value Buyers
        return f"""
        - Reduce friction and risk
        This customer purchased only {frequency_last_year} times in the last year and generates ${annual_value} annually. Offer low-commitment incentives such as free shipping, small bundles, or first-repeat discounts to encourage a second purchase.

        - Trigger reactivation quickly
        With {days_since_last_purchase} days since their last order, deploy short, time-bound reactivation campaigns focused on ease, value, and reassurance rather than upsell.

        - Test engagement before heavy investment
        Monitor response to lightweight campaigns before allocating higher-cost incentives. Customers who re-engage can be upgraded into higher-touch strategies; non-responders should remain in automated flows.
        """
    