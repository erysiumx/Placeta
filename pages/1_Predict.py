import streamlit as st
import re

st.set_page_config(page_title="Placeta | Predict", layout="wide")

st.title("Predict Placental Transfer")
st.markdown("Enter a valid SMILES string or compound name to generate a baseline profile.")

# User Input
user_input = st.text_input("Compound Input (Name or SMILES)", placeholder="e.g., Sertraline or CN[C@@H]1CC[C@H](c2ccc(Cl)c(Cl)c2)c3ccccc13")

# Simple Gibberish / Validation Check Function
def is_likely_gibberish(text):
    # If it's too short, has no letters, or is just random symbols
    if len(text) < 2: return True
    if not re.search('[a-zA-Z]', text): return True
    # If it looks like keyboard mashing without chemical syntax
    if re.match(r'^[asdfghjklqwertyuiopzxcvbnm]+$', text.lower()) and len(text) > 8: return True
    return False

if user_input:
    if is_likely_gibberish(user_input):
        st.error("Compound not identified. Please enter a valid chemical name or SMILES string.")
    else:
        st.success(f"Compound identified: {user_input}")
        st.markdown("*(Model prediction execution logic will execute here)*")
        
        # Display aesthetic placeholder metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Baseline Transfer Score", "--")
        col2.metric("Uncertainty Domain", "--")
        col3.metric("Applicability Flag", "--")
