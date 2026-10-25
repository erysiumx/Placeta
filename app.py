import streamlit as st
from PIL import Image
import os

# Minimalist configuration: No icons, strict naming
st.set_page_config(page_title="Placeta", layout="wide")

# Sidebar with image and explicit scientific disclaimers
img_path = "a87edb60-d8a1-4118-a063-3dce881919a9.jpeg"
if os.path.exists(img_path):
    img = Image.open(img_path)
    st.sidebar.image(img, use_container_width=True) 

st.sidebar.markdown("---")
st.sidebar.markdown("### Placeta Framework")
st.sidebar.markdown(
    "<div style='font-size: 0.85em; color: #F8F9FA; background-color: #112240; padding: 10px; border-left: 3px solid #2A7B9B;'>"
    "<b>PRECAUTIONARY STATEMENT:</b><br>"
    "This platform is a hypothesis-generating research prototype evaluating placental transfer predictions. "
    "It is strictly <b>not</b> intended for clinical dosing, regulatory submission, or pregnancy-safety decision making."
    "</div>", unsafe_allow_html=True
)

# Main Homepage Content
st.title("Placeta")
st.markdown("#### Bridging In Vitro Benchmarks and Clinical Placental Exposure")

st.markdown("""
Welcome to the Placeta research prototype. 

This environment operationalizes the discrepancy between standard 2D QSAR permeability liability and dynamic human umbilical-to-maternal (U/M) exposure.

**Core Modules:**
* **Predict:** Evaluate baseline transfer scores and apply literature-informed scenario modifiers.
* **Explore:** Analyze discrepancies between baseline predictions and verified clinical observations.
* **Prioritize:** View the active-learning engine prioritizing compounds for future literature curation.

*Use the sidebar to navigate the modules.*
""")
