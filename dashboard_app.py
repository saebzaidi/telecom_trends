import os
import sys
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import webbrowser
import threading
import time

# --- STREAMLIT CONFIG FIXES ---
#st.set_option('server.enableCORS', False)
#st.set_option('server.enableXsrfProtection', False)
#st.set_option('server.headless', True)

# --- AUTO OPEN BROWSER ---
#def open_browser():
    # Wait a bit for Streamlit server to start
#    time.sleep(2)
#    webbrowser.open_new("http://localhost:8501")

#threading.Thread(target=open_browser).start()

# --- APP CONFIG ---
st.set_page_config(page_title="Telecom Trends Dashboard", layout="wide")
st.title("📊 Telecom Indicators Trends Explorer")

st.markdown("""
This interactive tool allows you to explore telecom indicators by country and year.  
The Excel file is already packaged — just click below to start exploring.
""")

# --- LOAD PACKAGED EXCEL FILE ---
# Detect the correct path whether running as script or bundled .exe
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS  # PyInstaller extraction path
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

excel_path = os.path.join(base_path, "telecom_data.xlsx")

try:
    df = pd.read_excel(excel_path)
except Exception as e:
    st.error(f"❌ Could not load Excel file: {e}")
    st.stop()

# Basic cleanup
df.columns = [str(c).strip() for c in df.columns]

# Show preview
with st.expander("🔍 Preview Data"):
    st.dataframe(df.head(20))

# --- Validate structure ---
required_cols = {"REF_AREA_LABEL", "INDICATOR_LABEL"}
if not required_cols.issubset(df.columns):
    st.error("❌ Excel file must contain at least 'REF_AREA_LABEL' and 'INDICATOR_LABEL' columns.")
    st.stop()

year_cols = [col for col in df.columns if str(col).isdigit()]
if not year_cols:
    st.error("❌ No year columns detected. Ensure your file includes columns like 2000, 2001, ... 2024.")
    st.stop()

# --- Sidebar filters ---
st.sidebar.header("🔎 Filter Options")
areas = sorted(df["REF_AREA_LABEL"].dropna().unique().tolist())
indicators = sorted(df["INDICATOR_LABEL"].dropna().unique().tolist())

selected_area = st.sidebar.selectbox("Select Country / AREA:", areas)
selected_indicator = st.sidebar.selectbox("Select Indicator:", indicators)

# --- Filtered data ---
filtered_df = df[(df["REF_AREA_LABEL"] == selected_area) & (df["INDICATOR_LABEL"] == selected_indicator)]

if filtered_df.empty:
    st.warning("⚠️ No data found for this combination.")
else:
    # Melt for plotting
    trend_df = filtered_df.melt(
        id_vars=["REF_AREA_LABEL", "INDICATOR_LABEL"],
        value_vars=year_cols,
        var_name="Year",
        value_name="Value"
    )
    trend_df["Year"] = trend_df["Year"].astype(int)

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(trend_df["Year"], trend_df["Value"], marker="o", linestyle="-")
    ax.set_title(f"{selected_indicator}\n({selected_area})", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Value")
    ax.grid(True)

    st.pyplot(fig)

    # --- Statistics summary ---
    st.markdown("### 📈 Indicator Summary")
    st.write(trend_df.describe())

    # --- Option to export filtered data ---
    csv = trend_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="💾 Download this trend data as CSV",
        data=csv,
        file_name=f"{selected_area}_{selected_indicator}_trend.csv",
        mime="text/csv"
    )
