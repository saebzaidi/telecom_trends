import os
import time
import webbrowser
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
#  AUTO-OPEN IN BROWSER (only used for local runs)
# ==========================================================
def open_browser():
    """Automatically open the app in the default browser (local runs only)."""
    time.sleep(2)
    webbrowser.open_new("http://localhost:8501")


# ==========================================================
#  DATA LOADING
# ==========================================================
def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_path, "telecom_data.xlsx")

    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        st.error(f"❌ Could not load Excel file: {e}")
        st.stop()

    return df


# ==========================================================
#  DASHBOARD
# ==========================================================
def draw_dashboard(df):
    st.set_page_config(page_title="Telecom Trends Dashboard", layout="wide")
    st.title("📊 Telecom Indicators Trends Explorer")

    st.markdown("""
    This interactive tool allows you to explore telecom indicators by country and year.  
    Upload or use the existing `telecom_data.xlsx` to begin exploring.
    """)

    # Normalize column names
    df.columns = [str(c).strip() for c in df.columns]

    with st.expander("🔍 Preview Data"):
        st.dataframe(df.head(20))

    # Validate structure
    required_cols = {"REF_AREA_LABEL", "INDICATOR_LABEL"}
    if not required_cols.issubset(df.columns):
        st.error("❌ Excel must contain 'REF_AREA_LABEL' and 'INDICATOR_LABEL' columns.")
        st.stop()

    year_cols = [col for col in df.columns if str(col).isdigit()]
    if not year_cols:
        st.error("❌ No year columns detected. Ensure your file includes columns like 2000, 2001, ... 2024.")
        st.stop()

    # Sidebar filters
    st.sidebar.header("🔎 Filter Options")
    areas = sorted(df["REF_AREA_LABEL"].dropna().unique().tolist())
    indicators = sorted(df["INDICATOR_LABEL"].dropna().unique().tolist())

    selected_areas = st.sidebar.multiselect(
        "Select up to 5 Areas / Countries",
        options=areas,
        default=areas[:1],
        max_selections=5
    )
    selected_indicator = st.sidebar.selectbox("Select Indicator:", indicators)

    # Filter data
    if selected_areas and selected_indicator:
        filtered_df = df[
            (df["REF_AREA_LABEL"].isin(selected_areas)) &
            (df["INDICATOR_LABEL"] == selected_indicator)
        ]

        if filtered_df.empty:
            st.warning("⚠️ No data found for this combination.")
            return

        # Melt for trend plotting
        trend_df = filtered_df.melt(
            id_vars=["REF_AREA_LABEL", "INDICATOR_LABEL"],
            value_vars=year_cols,
            var_name="Year",
            value_name="Value"
        )
        trend_df["Year"] = trend_df["Year"].astype(int)

        # Plot
        fig, ax = plt.subplots(figsize=(10, 6))
        for area in selected_areas:
            sub_df = trend_df[trend_df["REF_AREA_LABEL"] == area]
            ax.plot(sub_df["Year"], sub_df["Value"], marker="o", label=area)

        ax.set_title(f"{selected_indicator} Comparison")
        ax.set_xlabel("Year")
        ax.set_ylabel("Value")
        ax.legend(title="Area / Country")
        ax.grid(True, linestyle="--", alpha=0.6)
        st.pyplot(fig)

        # Summary stats
        st.markdown("### 📈 Indicator Summary")
        st.write(trend_df.describe())

        # Download CSV
        csv = trend_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="💾 Download this trend data as CSV",
            data=csv,
            file_name=f"{selected_indicator}_trend.csv",
            mime="text/csv"
        )

    else:
        st.info("Please select at least one country and indicator to view results.")

    st.markdown("---")
    st.caption("Developed by Saeb Zaidi © 2025")


# ==========================================================
#  MAIN ENTRY POINT
# ==========================================================
def main():
    data = load_data()
    draw_dashboard(data)


# ==========================================================
#  EXECUTION LOGIC
# ==========================================================
if __name__ == "__main__":
    # Only auto-open browser if running locally (not on Streamlit Cloud)
    if "streamlit" not in os.environ.get("STREAMLIT_RUNTIME", "").lower():
        import threading
        threading.Thread(target=open_browser, daemon=True).start()

    main()


