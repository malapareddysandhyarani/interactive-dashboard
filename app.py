import streamlit as st
import pandas as pd
import numpy as np
import datetime

# Import custom helper modules
import utils
import charts
import db

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM CSS STYLING
# -------------------------------------------------------------
st.set_page_config(
    page_title="Interactive Business Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphism CSS styling
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Banner */
    .main-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
        padding: 24px 30px;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        color: #cbd5e1;
        font-size: 1.05rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    
    /* KPI Card Container */
    .kpi-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px;
        text-align: left;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 20px -5px rgba(99, 102, 241, 0.25);
        border-color: #6366f1;
    }
    
    .kpi-icon {
        font-size: 1.8rem;
        float: right;
        opacity: 0.85;
    }
    
    .kpi-title {
        color: #94a3b8;
        font-size: 0.88rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        color: #f8fafc;
        font-size: 1.85rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .kpi-subtext {
        color: #10b981;
        font-size: 0.82rem;
        font-weight: 500;
    }
    
    /* Search Bar & Badge Styling */
    .stTextInput > div > div > input {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.3) !important;
    }
    
    /* Custom Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
        color: #ffffff;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #4338ca 0%, #4f46e5 100%);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1e293b;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #334155;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        padding: 0 20px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #312e81 !important;
        color: #ffffff !important;
        border: 1px solid #6366f1;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. LOAD DATASET & DATABASE CONNECTION STATUS
# -------------------------------------------------------------
raw_df = utils.load_data()

# -------------------------------------------------------------
# 3. SIDEBAR FILTERS & DATABASE STATUS
# -------------------------------------------------------------
st.sidebar.markdown("### 🎛️ Dashboard Filters")
st.sidebar.markdown("---")

# Database Connection Status Badge
db_ok, db_msg = db.test_connection()
if db_ok:
    st.sidebar.success("🟢 **Neon PostgreSQL**: Connected", icon="🐘")
else:
    st.sidebar.warning("⚠️ **Database**: Offline (CSV Fallback)", icon="📁")

if st.sidebar.button("🔄 Sync with Neon DB", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")

# Date Range Filter
min_date = raw_df["Date"].min().date()
max_date = raw_df["Date"].max().date()

st.sidebar.markdown("**📅 Select Date Range**")
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    label_visibility="collapsed"
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Category Filter
all_categories = sorted(raw_df["Category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "📦 Category",
    options=["All"] + all_categories,
    default=["All"]
)

# Region Filter
all_regions = sorted(raw_df["Region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect(
    "🌍 Region",
    options=["All"] + all_regions,
    default=["All"]
)

# Rating Filter
min_rating_val = float(raw_df["Customer_Rating"].min())
max_rating_val = float(raw_df["Customer_Rating"].max())

rating_range = st.sidebar.slider(
    "⭐ Customer Rating Filter",
    min_value=min_rating_val,
    max_value=max_rating_val,
    value=(min_rating_val, max_rating_val),
    step=0.5
)

# Render mode toggle in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("**🎨 Chart Render Engine**")
chart_engine = st.sidebar.radio(
    "Select Plotting Library",
    options=["Matplotlib / Seaborn", "Plotly (Interactive)"],
    index=0
)

# Filter Data
filtered_df = utils.filter_data(
    raw_df,
    start_date=start_date,
    end_date=end_date,
    categories=selected_categories,
    regions=selected_regions,
    min_rating=rating_range[0],
    max_rating=rating_range[1]
)

# -------------------------------------------------------------
# 4. MAIN HEADER & HOME PAGE OVERVIEW
# -------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>📈 Executive Business Analytics Dashboard</h1>
    <p>Real-time tracking of revenues, sales categories, regional distributions, and product performance.</p>
</div>
""", unsafe_allow_html=True)

# Calculate KPIs for home page
kpis = utils.calculate_kpis(filtered_df)

# Home Page KPI Cards (Total Records, Total Revenue, Average Rating, Total Categories)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <span class="kpi-icon">📋</span>
        <div class="kpi-title">Total Records</div>
        <div class="kpi-value">{kpis['total_records']:,}</div>
        <div class="kpi-subtext">Filtered Orders</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <span class="kpi-icon">💰</span>
        <div class="kpi-title">Total Revenue</div>
        <div class="kpi-value">${kpis['total_revenue']:,.2f}</div>
        <div class="kpi-subtext">Profit: ${kpis['total_profit']:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <span class="kpi-icon">⭐</span>
        <div class="kpi-title">Average Rating</div>
        <div class="kpi-value">{kpis['avg_rating']:.2f} / 5.0</div>
        <div class="kpi-subtext">Customer Feedback</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <span class="kpi-icon">🏷️</span>
        <div class="kpi-title">Total Categories</div>
        <div class="kpi-value">{kpis['total_categories']}</div>
        <div class="kpi-subtext">Product Lines</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 5. DASHBOARD NAVIGATION TABS
# -------------------------------------------------------------
tab_overview, tab_charts, tab_data = st.tabs([
    "ℹ️ Dataset Overview & Summary",
    "📊 Business Analytics (5 Charts)",
    "📁 Raw Data & Search Engine"
])

# =============================================================
# TAB 1: DATASET OVERVIEW (Home Page Requirement)
# =============================================================
with tab_overview:
    st.markdown("### 📋 Dataset Overview")
    st.info("Comprehensive breakdown of dataset attributes, data types, and total record counts.")
    
    overview_meta = utils.get_dataset_info(filtered_df)
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Total Rows Count", f"{overview_meta['num_rows']:,}")
    m_col2.metric("Total Columns Count", overview_meta['num_cols'])
    m_col3.metric("Memory Usage", f"{overview_meta['memory_usage_kb']} KB")
    m_col4.metric("Date Span", f"2024 to 2026")
    
    st.markdown("---")
    
    ov_c1, ov_c2 = st.columns([1, 1])
    
    with ov_c1:
        st.markdown("#### 🔤 Column Attributes & Data Types")
        dtype_df = pd.DataFrame({
            "Column Name": overview_meta["columns"],
            "Data Type": [overview_meta["dtypes"][col] for col in overview_meta["columns"]],
            "Missing Values": [overview_meta["missing_values"][col] for col in overview_meta["columns"]]
        })
        st.dataframe(dtype_df, use_container_width=True, hide_index=True)
        
    with ov_c2:
        st.markdown("#### 🔢 Numerical Summary Statistics")
        st.dataframe(filtered_df.describe().T[["mean", "std", "min", "50%", "max"]], use_container_width=True)

# =============================================================
# TAB 2: 5 REQUIRED CHARTS
# =============================================================
with tab_charts:
    st.markdown("### 📊 Interactive Visual Analytics")
    st.caption(f"Currently Rendering with **{chart_engine}** engine. Use the sidebar to switch renderers or filters.")
    
    # ------------------ CHART 1: LINE CHART ------------------
    st.markdown("#### 1️⃣ Line Chart: Sales & Profit Trend Over Time")
    lc_c1, lc_c2 = st.columns([3, 1])
    with lc_c2:
        freq_option = st.selectbox("Granularity", ["Monthly", "Weekly", "Daily"], index=0)
        freq_code = "ME" if freq_option == "Monthly" else ("W" if freq_option == "Weekly" else "D")
    
    with lc_c1:
        if chart_engine == "Matplotlib / Seaborn":
            fig_line = charts.plot_line_chart_seaborn(filtered_df, freq=freq_code)
            st.pyplot(fig_line, use_container_width=True)
        else:
            fig_line = charts.plot_line_chart_plotly(filtered_df, freq=freq_code)
            st.plotly_chart(fig_line, use_container_width=True)
            
    st.markdown("---")
    
    # ------------------ CHARTS 2 & 3: BAR CHART & HEATMAP ------------------
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.markdown("#### 2️⃣ Bar Chart: Category Comparison")
        bar_metric = st.radio("Bar Metric", ["Revenue", "Profit", "Quantity"], horizontal=True)
        if chart_engine == "Matplotlib / Seaborn":
            fig_bar = charts.plot_bar_chart_seaborn(filtered_df, metric=bar_metric)
            st.pyplot(fig_bar, use_container_width=True)
        else:
            fig_bar = charts.plot_bar_chart_plotly(filtered_df, metric=bar_metric)
            st.plotly_chart(fig_bar, use_container_width=True)
            
    with row2_col2:
        st.markdown("#### 3️⃣ Heatmap: Feature Correlation Matrix")
        st.write("") # spacing
        if chart_engine == "Matplotlib / Seaborn":
            fig_heat = charts.plot_heatmap_seaborn(filtered_df)
            st.pyplot(fig_heat, use_container_width=True)
        else:
            fig_heat = charts.plot_heatmap_plotly(filtered_df)
            st.plotly_chart(fig_heat, use_container_width=True)
            
    st.markdown("---")
    
    # ------------------ CHARTS 4 & 5: PIE CHART & HISTOGRAM ------------------
    row3_col1, row3_col2 = st.columns(2)
    
    with row3_col1:
        st.markdown("#### 4️⃣ Pie Chart: Regional Revenue Distribution")
        if chart_engine == "Matplotlib / Seaborn":
            fig_pie = charts.plot_pie_chart_seaborn(filtered_df)
            st.pyplot(fig_pie, use_container_width=True)
        else:
            fig_pie = charts.plot_pie_chart_plotly(filtered_df)
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with row3_col2:
        st.markdown("#### 5️⃣ Histogram: Frequency Distribution")
        hist_var = st.selectbox("Select Attribute for Histogram", ["Customer_Rating", "Revenue", "Profit", "Quantity"])
        if chart_engine == "Matplotlib / Seaborn":
            fig_hist = charts.plot_histogram_seaborn(filtered_df, column=hist_var)
            st.pyplot(fig_hist, use_container_width=True)
        else:
            fig_hist = charts.plot_histogram_plotly(filtered_df, column=hist_var)
            st.plotly_chart(fig_hist, use_container_width=True)

# =============================================================
# TAB 3: DATASET SEARCH & CSV DOWNLOAD (Extra Features)
# =============================================================
with tab_data:
    st.markdown("### 🔍 Live Data Explorer & Export Engine")
    
    search_c1, search_c2 = st.columns([3, 1])
    with search_c1:
        search_query = st.text_input(
            "🔎 Search Bar (Filter by Product Name, Customer Name, Category, or Order ID)",
            placeholder="Type 'Earbuds', 'Emma', 'Electronics', or 'ORD-10025'...",
            key="search_input"
        )
    
    searched_df = utils.search_dataset(filtered_df, search_query)
    
    with search_c2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        # Download filtered data as CSV
        csv_data = searched_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered CSV",
            data=csv_data,
            file_name=f"filtered_business_data_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    st.caption(f"Showing **{len(searched_df)}** matching records out of **{len(filtered_df)}** filtered records.")
    
    # Display dataset dataframe with formatted view
    st.dataframe(
        searched_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Revenue": st.column_config.NumberColumn("Revenue", format="$%.2f"),
            "Profit": st.column_config.NumberColumn("Profit", format="$%.2f"),
            "Unit_Price": st.column_config.NumberColumn("Unit Price", format="$%.2f"),
            "Discount_Pct": st.column_config.NumberColumn("Discount", format="%.0f%%"),
            "Customer_Rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐")
        }
    )
