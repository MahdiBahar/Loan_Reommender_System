def calculate_monthly_repayment(loan_amount, annual_interest_rate, repayment_duration_months):
    """
    Calculate the monthly repayment amount for a loan using the formula from the Excel file.

    :param loan_amount: Total loan amount (principal)
    :param annual_interest_rate: Annual interest rate (in percentage, e.g., 23 for 23%)
    :param repayment_duration_months: Loan repayment duration in months
    :return: Monthly repayment amount
    """
    # Convert annual interest rate to monthly interest rate (decimal)
    monthly_interest_rate = (annual_interest_rate / (12*100))
    

    # Apply the formula from the Excel file
    numerator = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** repayment_duration_months
    denominator = ((1 + monthly_interest_rate) ** repayment_duration_months) - 1
    monthly_repayment = numerator / denominator

    return monthly_repayment

# Example usage
loan_amount = 2_000_000_000  # 1 billion
annual_interest_rate = 23  # 23%
repayment_duration_months = 36  # 36 months

monthly_repayment = calculate_monthly_repayment(loan_amount, annual_interest_rate, repayment_duration_months)
total_repayment = monthly_repayment * repayment_duration_months

print(f"Monthly repayment amount: {monthly_repayment:,.2f}")
print(f"Total repayment amount: {total_repayment:,.2f}")