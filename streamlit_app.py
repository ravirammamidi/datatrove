import streamlit as st
import pandas as pd
import json

def compare_json(json1, json2, path=""):
    """Compare two JSON objects and return the missing keys and differing values in both."""
    missing_in_json1 = []
    missing_in_json2 = []
    differing_values = []

    for key in json1:
        if key not in json2:
            missing_in_json2.append(f"{path}/{key}")
        elif isinstance(json1[key], dict) and isinstance(json2[key], dict):
            sub_missing1, sub_missing2, sub_diffs = compare_json(json1[key], json2[key], path=f"{path}/{key}")
            missing_in_json1.extend(sub_missing1)
            missing_in_json2.extend(sub_missing2)
            differing_values.extend(sub_diffs)
        elif json1[key] != json2[key]:
            differing_values.append(f"{path}/{key}: {json1[key]} != {json2[key]}")

    for key in json2:
        if key not in json1:
            missing_in_json1.append(f"{path}/{key}")

    return missing_in_json1, missing_in_json2, differing_values

def prettify_json(json_str):
    try:
        parsed_json = json.loads(json_str)
        # Sort keys and use an indentation of 4 for the prettified JSON
        prettified_json = json.dumps(parsed_json, indent=4, sort_keys=True)
        return True, prettified_json
    except json.JSONDecodeError as e:
        return False, str(e)
    
def car_loan_total_cost(car_cost, down_payment, annual_apr, loan_term_years):
    # Calculate the loan amount
    loan_amount = car_cost - down_payment
    
    # Convert APR to a decimal and calculate monthly interest rate
    monthly_interest_rate = (annual_apr / 100) / 12
    
    # Calculate the number of monthly payments
    total_payments = loan_term_years * 12
    
    # Calculate monthly payment using the formula for an installment loan
    if monthly_interest_rate > 0:
        monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** total_payments) / ((1 + monthly_interest_rate) ** total_payments - 1)
    else:
        monthly_payment = loan_amount / total_payments
    
    # Calculate the total amount paid over the loan term
    total_paid = monthly_payment * total_payments
    
    # Add the down payment to the total amount paid
    total_cost = total_paid + down_payment
    
    return total_cost, total_paid, loan_amount, monthly_payment

def main():
    st.title("JSON Comparator")

    col1, col2 = st.columns(2)
    
    with col1:
        # Note the unique key for the text area
        json_str1 = st.text_area("Paste JSON 1", height=300, key="json_input_1")
        
    with col2:
        # Note the unique key for the text area
        json_str2 = st.text_area("Paste JSON 2", height=300, key="json_input_2")

    if st.button('Prettify & Check Syntax'):
        success1, result1 = prettify_json(json_str1)
        success2, result2 = prettify_json(json_str2)

        if success1:
            st.session_state['prettified_json1'] = result1  # Use unique session state key
        else:
            st.error(f"JSON 1 Syntax Error: {result1}")
        
        if success2:
            st.session_state['prettified_json2'] = result2  # Use unique session state key
        else:
            st.error(f"JSON 2 Syntax Error: {result2}")

        if success1 and success2:
            st.success("Both JSON inputs are valid and have been prettified.")

    if st.button('Compare'):
        if 'prettified_json1' in st.session_state and 'prettified_json2' in st.session_state:
            try:
                json1 = json.loads(st.session_state['prettified_json1'])
                json2 = json.loads(st.session_state['prettified_json2'])

                missing_in_json1, missing_in_json2, differing_values = compare_json(json1, json2)

                if missing_in_json1 or missing_in_json2 or differing_values:
                    if missing_in_json1:
                        with st.expander("Missing in JSON 1"):
                            for item in missing_in_json1:
                                st.markdown(f"- `{item}`")
                    
                    if missing_in_json2:
                        with st.expander("Missing in JSON 2"):
                            for item in missing_in_json2:
                                st.markdown(f"- `{item}`")
                    
                    if differing_values:
                        with st.expander("Differing Values"):
                            for item in differing_values:
                                st.markdown(f"- `{item}`")
                else:
                    st.success("No missing attributes or differing values found!")
            except json.JSONDecodeError:
                st.error("An unexpected error occurred while comparing JSONs.")
        else:
            st.error("Please prettify & check syntax before comparing.")

    st.title("Car Loan Total Cost Calculator")

    car_cost = st.number_input("Enter the total cost of the car:", min_value=0.0, format="%.2f")
    down_payment = st.number_input("Enter the down payment:", min_value=0.0, format="%.2f")
    annual_apr = st.number_input("Enter the annual interest rate (APR) in percent:", min_value=0.0, format="%.2f")
    loan_term_years = st.number_input("Enter the loan term in years:", min_value=1, format="%d")

    if st.button("Calculate Total Cost"):
        total_cost, total_paid, loan_amount, monthly_payment = car_loan_total_cost(car_cost, down_payment, annual_apr, loan_term_years)
        interest_paid = total_paid - loan_amount
        down_payment_percent = (down_payment / total_cost) * 100
        loan_amount_percent = (loan_amount / total_cost) * 100
        interest_paid_percent = (interest_paid / total_cost) * 100

        # Calculate the true cost of owning the car per month
        true_cost_per_month = monthly_payment

        st.write(f"The total cost paid after the end of the loan period is: ${total_cost:.2f}")
        st.write(f"The true cost of owning the car per month is: ${true_cost_per_month:.2f}")

        # Create breakdown data for the total term of the loan
        breakdown_data = {
            'Category': ['Down Payment', 'Loan Amount', 'Interest Paid'],
            'Amount': [down_payment, loan_amount, interest_paid]
        }
        breakdown_df = pd.DataFrame(breakdown_data)

        # Display the breakdown of costs over the total term of the loan
        st.write("Breakdown of Costs Over the Total Term of the Loan:")
        st.bar_chart(breakdown_df.set_index('Category'))

if __name__ == "__main__":
    main()
