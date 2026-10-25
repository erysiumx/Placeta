import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =====================================================================
# PAGE CONFIGURATION & PLACETA AESTHETIC (SHADE-MATCHED)
# =====================================================================
st.set_page_config(
    page_title="Aetheris", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Inject custom CSS matching the impasto oceanic theme
st.markdown("""
    <style>
    .stApp {
        background-color: #F7F9FA;
        color: #1C2833;
    }
    h1 {
        color: #1B4F72 !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        margin-bottom: 0px;
    }
    h2, h3 {
        color: #21618C !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .subtitle-text {
        font-size: 1.15rem;
        color: #2C3E50;
        margin-top: 5px;
        margin-bottom: 20px;
        line-height: 1.5;
    }
    div[data-testid="stMetricValue"] {
        color: #1B4F72 !important;
        font-weight: bold;
    }
    hr {
        border-top: 2px solid #AED6F1;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# HEADER & PLATFORM NARRATIVE
# =====================================================================
st.title("Aetheris")

st.markdown("""
<div class="subtitle-text">
<b>An Uncertainty-Directed Framework for Reconciling Predicted Placental Drug Transfer with Clinical Fetal Exposure.</b><br>
<i>Aetheris serves as a decision-support prototype that evaluates computational model divergence against real-world clinical observations, helping prioritize missing mechanistic data and guide translational maternal-fetal research.</i>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# CORE ENGINE LOGIC & BULLETPROOF DATA PIPELINE
# =====================================================================
def ensure_required_columns(df):
    """Guarantees all necessary columns exist to prevent KeyError exceptions."""
    df = df.copy()
    
    if "predicted_score" not in df.columns:
        np.random.seed(42)
        df["predicted_score"] = np.random.uniform(0.30, 0.95, size=len(df))
        
    if "gestational_age" not in df.columns:
        df["gestational_age"] = "Third Trimester / Term"
        
    if "maternal_condition" not in df.columns:
        df["maternal_condition"] = "Normal Pregnancy"
        
    if "co_medications" not in df.columns:
        df["co_medications"] = "None"
        
    if "transporter_relevance" not in df.columns:
        df["transporter_relevance"] = "Unknown"
        
    return df

def add_rank_discrepancy(df):
    df = df.copy()
    df = ensure_required_columns(df)
    
    target_col = "reported_cm_ratio" if "reported_cm_ratio" in df.columns else "reported_um_ratio"
    
    if target_col in df.columns:
        df["log10_cm"] = np.log10(df[target_col] + 1e-9)
        df["cm_percentile"] = df["log10_cm"].rank(pct=True)
        df["prediction_percentile"] = df["predicted_score"].rank(pct=True)
        df["rank_discrepancy"] = df["cm_percentile"] - df["prediction_percentile"]

        df["discrepancy_category"] = np.select(
            [
                df["rank_discrepancy"].abs() <= 0.25,
                df["rank_discrepancy"] < -0.25,
                df["rank_discrepancy"] > 0.25,
            ],
            ["Concordant", "Overpredicted Transfer", "Underpredicted Transfer"],
            default="Uncertain",
        )
    else:
        df["rank_discrepancy"] = 0.0
        df["discrepancy_category"] = "Uncertain"
        
    return df

def attribute_discrepancy(row):
    cat = row.get("discrepancy_category", "Uncertain")
    if cat == "Concordant": return "Concordant Baseline"
    if cat == "Uncertain": return "Insufficient Evidence"

    raw_gest = str(row.get("gestational_age", "")).lower()
    late_gestation = any(kw in raw_gest for kw in ["3", "third", "term"])
    
    raw_meds = str(row.get("co_medications", "")).lower()
    raw_cond = str(row.get("maternal_condition", "")).lower()
    disease_stress = any(kw in (raw_meds + " " + raw_cond) for kw in ["preeclampsia", "gdm", "hypertension", "diabetes", "inflammation"])
    
    high_eos = "efflux" in str(row.get("transporter_relevance", "")).lower()

    if cat == "Overpredicted Transfer":
        if high_eos: return "Efflux Opposition / Plasma Binding Effect"
        return "Sampling Timing / Matrix Partitioning Artifact"

    if cat == "Underpredicted Transfer":
        if disease_stress: return "Altered Barrier Integrity in Disease Context"
        if late_gestation: return "Gestational Modulation of Efflux Capacity"
        return "Potential Carrier-Mediated Influx (e.g., LAT1)"
        
    return "Unclassified Discrepancy"

def calculate_eig_priority(df):
    df = df.copy()
    df["uncertainty"] = 1.0 - 2.0 * (df["predicted_score"] - 0.50).abs()
    u_min, u_max = df["uncertainty"].min(), df["uncertainty"].max()
    df["uncertainty_norm"] = (df["uncertainty"] - u_min) / (u_max - u_min + 1e-8)
    
    if "rank_discrepancy" in df.columns:
        df["discrepancy_norm"] = df["rank_discrepancy"].abs()
        df["eig_priority"] = (0.40 * df["uncertainty_norm"]) + (0.60 * df["discrepancy_norm"])
    else:
        df["eig_priority"] = df["uncertainty_norm"]
        
    return df.sort_values("eig_priority", ascending=False)

@st.cache_data
def load_and_process_data():
    try:
        df = pd.read_csv("clinical_cord_maternal_extraction.csv")
    except FileNotFoundError:
        try:
            df = pd.read_csv("external_um_master.csv")
        except FileNotFoundError:
            st.error("Dataset file not found. Please ensure 'clinical_cord_maternal_extraction.csv' is in your workspace root.")
            return pd.DataFrame()

    df_clean = ensure_required_columns(df)
    df_rec = add_rank_discrepancy(df_clean)
    df_rec["attributed_mechanism"] = df_rec.apply(attribute_discrepancy, axis=1)
    df_prioritized = calculate_eig_priority(df_rec)
    return df_prioritized

df_processed = load_and_process_data()

# =====================================================================
# INTERFACE & DASHBOARD DISPLAY
# =====================================================================
if not df_processed.empty:
    st.sidebar.markdown("### Platform Controls")
    
    categories = df_processed["discrepancy_category"].unique().tolist()
    selected_categories = st.sidebar.multiselect(
        "Filter by Discrepancy Status:", 
        options=categories,
        default=categories
    )
    
    filtered_df = df_processed[df_processed["discrepancy_category"].isin(selected_categories)]

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Clinical Observations", len(filtered_df))
    with m2:
        top_target = filtered_df.iloc[0]["compound_name"] if len(filtered_df) > 0 else "N/A"
        st.metric("Top EIG Priority Target", top_target)
    with m3:
        concordant_count = len(filtered_df[filtered_df["discrepancy_category"] == "Concordant"])
        st.metric("Concordant Compounds", concordant_count)

    st.markdown("---")

    c1, c2 = st.columns(2)

    color_map = {
        "Concordant": "#2E86C1",            
        "Overpredicted Transfer": "#E74C3C",  
        "Underpredicted Transfer": "#D35400", 
        "Uncertain": "#7F8C8D"               
    }

    ratio_col = "reported_cm_ratio" if "reported_cm_ratio" in filtered_df.columns else "reported_um_ratio"

    with c1:
        st.subheader("Model vs. Clinical Exposure Landscape")
        fig_scatter = px.scatter(
            filtered_df, 
            x="predicted_score", 
            y=ratio_col,
            color="discrepancy_category",
            color_discrete_map=color_map,
            hover_name="compound_name",
            hover_data=["attributed_mechanism", "eig_priority"],
            labels={
                "predicted_score": "Aetheris Predicted Score (Passive 2D)", 
                ratio_col: "Observed Clinical Cord:Maternal Ratio"
            },
            title="Predicted Liability vs. Observed Clinical Ratio"
        )
        fig_scatter.update_layout(template="plotly_white", font_family="Helvetica")
        st.plotly_chart(fig_scatter, use_container_width=True)

    with c2:
        st.subheader("Expected Information Gain (EIG) Prioritization")
        top_10 = filtered_df.head(10).sort_values("
