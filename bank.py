import streamlit as st
import pandas as pd
from datetime import datetime
import random

# --- Page Configuration ---
st.set_page_config(page_title="Bank Management System", page_icon="🏦", layout="centered")

# --- Initialize Session State (In-Memory Database) ---
if 'accounts' not in st.session_state:
    st.session_state.accounts = {}
    
# Account structure will be:
# { "account_number": { "name": "John Doe", "balance": 1000.0, "transactions": [ {"date": "...", "type": "Deposit", "amount": 1000.0} ] } }

# --- Helper Functions ---
def generate_account_number():
    """Generates a random 6-digit account number that doesn't already exist."""
    while True:
        acc_num = str(random.randint(100000, 999999))
        if acc_num not in st.session_state.accounts:
            return acc_num

def log_transaction(acc_num, trans_type, amount):
    """Logs a transaction into the account's history."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.accounts[acc_num]["transactions"].append({
        "Date": timestamp,
        "Type": trans_type,
        "Amount": amount
    })

# --- Main UI ---
st.title("🏦 Bank Account Management System")

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Choose an Action", 
    ["Create Account", "Deposit Funds", "Withdraw Funds", "Account Details & History"]
)

st.sidebar.markdown("---")
st.sidebar.info(f"Total Active Accounts: **{len(st.session_state.accounts)}**")

# --- 1. Create Account ---
if menu == "Create Account":
    st.header("📝 Create a New Account")
    
    with st.form("create_account_form", clear_on_submit=True):
        name = st.text_input("Full Name")
        initial_deposit = st.number_input("Initial Deposit Amount ($)", min_value=0.0, step=10.0, format="%.2f")
        submit_button = st.form_submit_button("Create Account")
        
        if submit_button:
            if not name.strip():
                st.error("Please enter a valid name.")
            else:
                acc_num = generate_account_number()
                st.session_state.accounts[acc_num] = {
                    "name": name.strip(),
                    "balance": initial_deposit,
                    "transactions": []
                }
                if initial_deposit > 0:
                    log_transaction(acc_num, "Initial Deposit", initial_deposit)
                    
                st.success(f"Account created successfully for {name}!")
                st.info(f"Your Account Number is: **{acc_num}** (Please save this!)")

# --- 2. Deposit Funds ---
elif menu == "Deposit Funds":
    st.header("💵 Deposit Funds")
    
    if not st.session_state.accounts:
        st.warning("No accounts exist yet. Please create an account first.")
    else:
        acc_list = list(st.session_state.accounts.keys())
        selected_acc = st.selectbox("Select Account Number", ["-- Select --"] + acc_list)
        
        if selected_acc != "-- Select --":
            acc_name = st.session_state.accounts[selected_acc]['name']
            st.write(f"**Account Holder:** {acc_name}")
            
            with st.form("deposit_form", clear_on_submit=True):
                deposit_amount = st.number_input("Amount to Deposit ($)", min_value=0.01, step=10.0, format="%.2f")
                deposit_btn = st.form_submit_button("Deposit")
                
                if deposit_btn:
                    st.session_state.accounts[selected_acc]["balance"] += deposit_amount
                    log_transaction(selected_acc, "Deposit", deposit_amount)
                    st.success(f"Successfully deposited ${deposit_amount:,.2f}!")
                    st.balloons()

# --- 3. Withdraw Funds ---
elif menu == "Withdraw Funds":
    st.header("🏧 Withdraw Funds")
    
    if not st.session_state.accounts:
        st.warning("No accounts exist yet. Please create an account first.")
    else:
        acc_list = list(st.session_state.accounts.keys())
        selected_acc = st.selectbox("Select Account Number", ["-- Select --"] + acc_list)
        
        if selected_acc != "-- Select --":
            acc_data = st.session_state.accounts[selected_acc]
            st.write(f"**Account Holder:** {acc_data['name']}")
            st.write(f"**Current Balance:** ${acc_data['balance']:,.2f}")
            
            with st.form("withdraw_form", clear_on_submit=True):
                withdraw_amount = st.number_input("Amount to Withdraw ($)", min_value=0.01, step=10.0, format="%.2f")
                withdraw_btn = st.form_submit_button("Withdraw")
                
                if withdraw_btn:
                    if withdraw_amount > acc_data["balance"]:
                        st.error("Insufficient Funds! You cannot withdraw more than your current balance.")
                    else:
                        st.session_state.accounts[selected_acc]["balance"] -= withdraw_amount
                        log_transaction(selected_acc, "Withdrawal", withdraw_amount)
                        st.success(f"Successfully withdrew ${withdraw_amount:,.2f}!")

# --- 4. Account Details & History ---
elif menu == "Account Details & History":
    st.header("📊 Account Details & Statement")
    
    if not st.session_state.accounts:
        st.warning("No accounts exist yet. Please create an account first.")
    else:
        acc_list = list(st.session_state.accounts.keys())
        selected_acc = st.selectbox("Select Account Number", ["-- Select --"] + acc_list)
        
        if selected_acc != "-- Select --":
            acc_data = st.session_state.accounts[selected_acc]
            
            # Display Account Summary
            st.subheader("Account Summary")
            col1, col2 = st.columns(2)
            col1.metric("Account Holder", acc_data["name"])
            col2.metric("Current Balance", f"${acc_data['balance']:,.2f}")
            
            st.markdown("---")
            
            # Display Transaction History
            st.subheader("Transaction History")
            transactions = acc_data["transactions"]
            
            if not transactions:
                st.info("No transactions found for this account.")
            else:
                # Convert list of dicts to Pandas DataFrame for a nice table display
                df = pd.DataFrame(transactions)
                # Format the Amount column to standard currency formatting
                df['Amount'] = df['Amount'].apply(lambda x: f"${x:,.2f}")
                
                st.dataframe(df, use_container_width=True, hide_index=True)