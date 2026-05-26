import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Permian AI Brain - MVP V1", layout="wide")
st.title("🧠 Permian AI Brain - MVP V1")
st.subheader("Midland Basin 5-Element Petroleum System Scanner (Your Backyard)")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Permian_Geochem_Midland_Heartland.csv")
    return df

df = load_data()

# 5-Element Scoring Function (physics-informed proxy)
def great_system_score(row):
    # 1. Prolific marine source rock (TOC)
    toc = pd.to_numeric(row.get('TOC'), errors='coerce')
    source_score = min(100, max(0, (toc - 1) * 25)) if pd.notna(toc) else 40

    # 2. Thermal maturity (Tmax) — safely convert to number
    tmax = pd.to_numeric(row.get('TMAX_C'), errors='coerce')
    thermal_score = 75 if pd.notna(tmax) and 435 <= tmax <= 465 else 45

    # 3. Generation potential (HI)
    hi = pd.to_numeric(row.get('HI'), errors='coerce')
    gen_score = 70 if pd.notna(hi) and hi > 150 else 40

    # 4. Seal proxy (based on formation)
    unit = str(row.get('SubsurfaceUnit', '')).lower()
    seal_score = 85 if any(x in unit for x in ['wolfcamp', 'bone spring', 'spraberry']) else 55

    # 5. Structure + Tectonic stability (base scores for Permian)
    struct_score = 75
    stability_score = 88

    # Final weighted score
    total = (source_score * 0.25 + 
             thermal_score * 0.20 + 
             gen_score * 0.20 + 
             seal_score * 0.15 + 
             struct_score * 0.10 + 
             stability_score * 0.10)
    
    return round(min(100, total), 1)

# Apply score
df['Great_Permian_System_Score'] = df.apply(great_system_score, axis=1)

# Sidebar filters
st.sidebar.header("Filters")
counties = st.sidebar.multiselect("County", options=df['CountyName'].unique(), default=df['CountyName'].unique())
formations = st.sidebar.multiselect("Formation", options=df['SubsurfaceUnit'].unique(), default=df['SubsurfaceUnit'].unique()[:5])

filtered = df[
    (df['CountyName'].isin(counties)) &
    (df['SubsurfaceUnit'].isin(formations) | (len(formations)==0))
]

# Dashboard
col1, col2 = st.columns([3, 2])
with col1:
    st.subheader("Top Ranked Prospects")
    top = filtered.sort_values('Great_Permian_System_Score', ascending=False).head(15)
    st.dataframe(top[['CountyName', 'SubsurfaceUnit', 'TOC', 'TMAX_C', 'HI', 'MinD_ft', 'Great_Permian_System_Score']], use_container_width=True)

with col2:
    st.subheader("Score Distribution")
    fig = px.histogram(filtered, x='Great_Permian_System_Score', nbins=20, color='CountyName', title="System Score by County")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Score Heatmap by County & Formation")
pivot = filtered.pivot_table(values='Great_Permian_System_Score', index='CountyName', columns='SubsurfaceUnit', aggfunc='mean').round(1)
st.dataframe(pivot, use_container_width=True)

st.success("✅ MVP V1 LIVE — Your AI brain is now scanning the heart of the Permian. Drop real well logs tomorrow and we go V2 with full PINN.")

st.caption("Built with your data • Midland/Odessa/Andrews/Kermit/Big Spring/Crane focus • Ready for PINN upgrade next")