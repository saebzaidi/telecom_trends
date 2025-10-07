import os
import sys
import subprocess
import threading
import webbrowser
import time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
#  AUTO-OPEN BROWSER (only once)
# ==========================================================
def open_browser():
    """Automatically open the app in the default browser"""
    time.sleep(2)
    webbrowser.open_new("http://localhost:8501")

# ==========================================================
#  STREAMLIT DASHBOARD CODE
# ==========================================================
def run_dashboard():
    # --- APP CONFIG ---
    st.set_page_config(page_title="Telecom Trends Dashboard", layout="wide")
    st.title("📊 Telecom Indicators Trends Explorer")

    st.markdown("""
    This interactive tool allows you to explore telecom indicators by country and year.  
    The Excel file is already packaged — just click below to start exploring.
    """)

    # --- LOAD PACKAGED EXCEL FILE ---
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

    # --- CLEANUP ---
    df.columns = [str(c).strip() for c in df.columns]

    # --- SHOW PREVIEW ---
    with st.expander("🔍 Preview Data"):
        st.dataframe(df.head(20))

    # --- VALIDATE STRUCTURE ---
    required_cols = {"REF_AREA_LABEL", "INDICATOR_LABEL"}
    if not required_cols.issubset(df.columns):
        st.error("❌ Excel file must contain at least 'REF_AREA_LABEL' and 'INDICATOR_LABEL' columns.")
        st.stop()

    year_cols = [col for col in df.columns if str(col).isdigit()]
    if not year_cols:
        st.error("❌ No year columns detected. Ensure your file includes columns like 2000, 2001, ... 2024.")
        st.stop()

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("🔎 Filter Options")
    areas = sorted(df["REF_AREA_LABEL"].dropna().unique().tolist())
    indicators = sorted(df["INDICATOR_LABEL"].dropna().unique().tolist())

    selected_area = st.sidebar.selectbox("Select Country / AREA:", areas)
    selected_indicator = st.sidebar.selectbox("Select Indicator:", indicators)

    # --- FILTERED DATA ---
    filtered_df = df[(df["REF_AREA_LABEL"] == selected_area) & (df["INDICATOR_LABEL"] == selected_indicator)]

    if filtered_df.empty:
        st.warning("⚠️ No data found for this combination.")
    else:
        # --- PREPARE TREND DATA ---
        trend_df = filtered_df.melt(
            id_vars=["REF_AREA_LABEL", "INDICATOR_LABEL"],
            value_vars=year_cols,
            var_name="Year",
            value_name="Value"
        )
        trend_df["Year"] = trend_df["Year"].astype(int)

        # --- PLOT ---
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(trend_df["Year"], trend_df["Value"], marker="o", linestyle="-")
        ax.set_title(f"{selected_indicator}\n({selected_area})", fontsize=14)
        ax.set_xlabel("Year")
        ax.set_ylabel("Value")
        ax.grid(True)
        st.pyplot(fig)

        # --- SUMMARY ---
        st.markdown("### 📈 Indicator Summary")
        st.write(trend_df.describe())

        # --- DOWNLOAD ---
        csv = trend_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="💾 Download this trend data as CSV",
            data=csv,
            file_name=f"{selected_area}_{selected_indicator}_trend.csv",
            mime="text/csv"
        )

# ==========================================================
#  MAIN EXECUTION
# ==========================================================
if __name__ == "__main__":
    # Start browser opener in background thread
    threading.Thread(target=open_browser).start()

    # If this file is executed as EXE -> run Streamlit subprocess
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        app_path = os.path.join(base_path, "app.py")
        cmd = [
            sys.executable,
            "-m", "streamlit", "run", app_path,
            "--server.fileWatcherType", "none"
        ]
        subprocess.run(cmd)
    else:
        # If running normally via Python -> run dashboard directly
        run_dashboard()
