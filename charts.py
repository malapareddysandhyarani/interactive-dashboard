import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as gg
import pandas as pd
import numpy as np

# Set global Seaborn & Matplotlib styling
plt.style.use('dark_background')
sns.set_theme(style="darkgrid", palette="muted")

# Custom sleek color palette
PALETTE = ["#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]

# -------------------------------------------------------------
# 1. LINE CHART: Sales & Profit Trend Over Time
# -------------------------------------------------------------
def plot_line_chart_seaborn(df, freq="ME"):
    """Seaborn/Matplotlib Line Chart showing Revenue & Profit trend over time."""
    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#0f172a")
    ax.set_facecolor("#1e293b")
    
    if df.empty:
        ax.text(0.5, 0.5, "No Data Available", color="white", ha="center", va="center", fontsize=14)
        return fig
    
    # Resample dataset by selected frequency (daily, weekly, monthly)
    df_temp = df.copy()
    df_temp["Date"] = pd.to_datetime(df_temp["Date"])
    df_grouped = df_temp.set_index("Date").resample(freq)[["Revenue", "Profit"]].sum().reset_index()
    
    sns.lineplot(data=df_grouped, x="Date", y="Revenue", label="Revenue ($)", color="#6366f1", linewidth=2.5, marker="o", ax=ax)
    sns.lineplot(data=df_grouped, x="Date", y="Profit", label="Profit ($)", color="#10b981", linewidth=2.5, marker="s", ax=ax)
    
    ax.set_title("Revenue & Profit Trend Over Time", fontsize=14, fontweight="bold", color="#f8fafc", pad=15)
    ax.set_xlabel("Date", fontsize=11, color="#94a3b8")
    ax.set_ylabel("Amount ($)", fontsize=11, color="#94a3b8")
    ax.tick_params(colors="#cbd5e1", labelsize=10)
    ax.grid(True, linestyle="--", alpha=0.3, color="#475569")
    ax.legend(facecolor="#1e293b", edgecolor="#475569", labelcolor="#f8fafc")
    
    plt.tight_layout()
    return fig

def plot_line_chart_plotly(df, freq="ME"):
    """Interactive Plotly Line Chart."""
    if df.empty:
        return px.line(title="No Data Available")
    
    df_temp = df.copy()
    df_temp["Date"] = pd.to_datetime(df_temp["Date"])
    df_grouped = df_temp.set_index("Date").resample(freq)[["Revenue", "Profit"]].sum().reset_index()
    
    fig = px.line(
        df_grouped, 
        x="Date", 
        y=["Revenue", "Profit"], 
        title="Revenue & Profit Trend Over Time (Interactive)",
        labels={"value": "Amount ($)", "variable": "Metric"},
        color_discrete_map={"Revenue": "#6366f1", "Profit": "#10b981"},
        markers=True
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        font=dict(color="#f8fafc"),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig

# -------------------------------------------------------------
# 2. BAR CHART: Category Comparison
# -------------------------------------------------------------
def plot_bar_chart_seaborn(df, metric="Revenue"):
    """Seaborn/Matplotlib Bar Chart comparing performance across product categories."""
    fig, ax = plt.subplots(figsize=(9, 4.8), facecolor="#0f172a")
    ax.set_facecolor("#1e293b")
    
    if df.empty:
        ax.text(0.5, 0.5, "No Data Available", color="white", ha="center", va="center", fontsize=14)
        return fig
    
    df_cat = df.groupby("Category")[metric].sum().reset_index().sort_values(by=metric, ascending=False)
    
    bars = sns.barplot(data=df_cat, x="Category", y=metric, palette="mako", ax=ax, hue="Category", legend=False)
    
    # Annotate bar values
    for bar in bars.patches:
        height = bar.get_height()
        label_text = f"${height:,.0f}" if metric == "Revenue" else f"{int(height):,}"
        ax.annotate(
            label_text,
            (bar.get_x() + bar.get_width() / 2., height),
            ha='center', va='bottom', fontsize=9, color='#e2e8f0', xytext=(0, 3),
            textcoords='offset points'
        )
        
    ax.set_title(f"Category Comparison by {metric}", fontsize=14, fontweight="bold", color="#f8fafc", pad=15)
    ax.set_xlabel("Category", fontsize=11, color="#94a3b8")
    ax.set_ylabel(metric, fontsize=11, color="#94a3b8")
    ax.tick_params(colors="#cbd5e1", labelsize=10)
    ax.grid(axis='y', linestyle="--", alpha=0.3, color="#475569")
    
    plt.tight_layout()
    return fig

def plot_bar_chart_plotly(df, metric="Revenue"):
    """Interactive Plotly Bar Chart."""
    if df.empty:
        return px.bar(title="No Data Available")
    
    df_cat = df.groupby("Category")[metric].sum().reset_index().sort_values(by=metric, ascending=False)
    
    fig = px.bar(
        df_cat,
        x="Category",
        y=metric,
        color="Category",
        text_auto=".2s" if metric == "Revenue" else True,
        title=f"Category Comparison by {metric} (Interactive)",
        color_discrete_sequence=PALETTE
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        font=dict(color="#f8fafc"),
        showlegend=False
    )
    return fig

# -------------------------------------------------------------
# 3. HEATMAP: Correlation Matrix
# -------------------------------------------------------------
def plot_heatmap_seaborn(df):
    """Seaborn Correlation Heatmap of numerical features."""
    fig, ax = plt.subplots(figsize=(7.5, 5.5), facecolor="#0f172a")
    ax.set_facecolor("#1e293b")
    
    num_cols = ["Revenue", "Profit", "Unit_Price", "Quantity", "Discount_Pct", "Customer_Rating"]
    valid_cols = [c for c in num_cols if c in df.columns]
    
    if df.empty or len(df) < 2:
        ax.text(0.5, 0.5, "Insufficient Data for Correlation", color="white", ha="center", va="center", fontsize=12)
        return fig
    
    corr = df[valid_cols].corr()
    
    sns.heatmap(
        corr, 
        annot=True, 
        fmt=".2f", 
        cmap="Blues", 
        cbar=True, 
        square=True, 
        linewidths=1, 
        linecolor="#0f172a",
        ax=ax,
        annot_kws={"size": 10, "weight": "bold"}
    )
    
    ax.set_title("Correlation Heatmap (Numerical Attributes)", fontsize=13, fontweight="bold", color="#f8fafc", pad=15)
    ax.tick_params(colors="#cbd5e1", labelsize=9.5)
    
    plt.tight_layout()
    return fig

def plot_heatmap_plotly(df):
    """Interactive Plotly Correlation Heatmap."""
    num_cols = ["Revenue", "Profit", "Unit_Price", "Quantity", "Discount_Pct", "Customer_Rating"]
    valid_cols = [c for c in num_cols if c in df.columns]
    
    if df.empty or len(df) < 2:
        return px.imshow([[0]], title="Insufficient Data")
    
    corr = df[valid_cols].corr()
    
    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="Plasma",
        title="Correlation Heatmap (Interactive)"
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        font=dict(color="#f8fafc")
    )
    return fig

# -------------------------------------------------------------
# 4. PIE / DONUT CHART: Regional Distribution
# -------------------------------------------------------------
def plot_pie_chart_seaborn(df):
    """Seaborn/Matplotlib Donut Chart showing revenue distribution by region."""
    fig, ax = plt.subplots(figsize=(6.5, 5), facecolor="#0f172a")
    
    if df.empty:
        ax.text(0.5, 0.5, "No Data Available", color="white", ha="center", va="center", fontsize=14)
        return fig
    
    df_reg = df.groupby("Region")["Revenue"].sum().reset_index()
    
    wedges, texts, autotexts = ax.pie(
        df_reg["Revenue"],
        labels=df_reg["Region"],
        autopct='%1.1f%%',
        startangle=140,
        colors=PALETTE[:len(df_reg)],
        wedgeprops=dict(width=0.4, edgecolor='#0f172a', linewidth=2),
        textprops=dict(color="#e2e8f0", fontsize=10)
    )
    
    for autotext in autotexts:
        autotext.set_color('#ffffff')
        autotext.set_weight('bold')
        
    ax.set_title("Revenue Distribution by Region", fontsize=14, fontweight="bold", color="#f8fafc", pad=15)
    
    plt.tight_layout()
    return fig

def plot_pie_chart_plotly(df):
    """Interactive Plotly Pie/Donut Chart."""
    if df.empty:
        return px.pie(title="No Data Available")
    
    df_reg = df.groupby("Region")["Revenue"].sum().reset_index()
    
    fig = px.pie(
        df_reg,
        names="Region",
        values="Revenue",
        hole=0.45,
        title="Revenue Distribution by Region (Interactive)",
        color_discrete_sequence=PALETTE
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        font=dict(color="#f8fafc")
    )
    return fig

# -------------------------------------------------------------
# 5. HISTOGRAM: Frequency Distribution
# -------------------------------------------------------------
def plot_histogram_seaborn(df, column="Customer_Rating"):
    """Seaborn Frequency Histogram with KDE curve."""
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="#0f172a")
    ax.set_facecolor("#1e293b")
    
    if df.empty:
        ax.text(0.5, 0.5, "No Data Available", color="white", ha="center", va="center", fontsize=14)
        return fig
    
    sns.histplot(
        data=df, 
        x=column, 
        kde=True, 
        color="#38bdf8", 
        bins=15 if column != "Customer_Rating" else 5, 
        edgecolor="#0f172a", 
        ax=ax
    )
    
    ax.set_title(f"Frequency Distribution of {column.replace('_', ' ')}", fontsize=14, fontweight="bold", color="#f8fafc", pad=15)
    ax.set_xlabel(column.replace('_', ' '), fontsize=11, color="#94a3b8")
    ax.set_ylabel("Count / Frequency", fontsize=11, color="#94a3b8")
    ax.tick_params(colors="#cbd5e1", labelsize=10)
    ax.grid(axis='y', linestyle="--", alpha=0.3, color="#475569")
    
    plt.tight_layout()
    return fig

def plot_histogram_plotly(df, column="Customer_Rating"):
    """Interactive Plotly Histogram."""
    if df.empty:
        return px.histogram(title="No Data Available")
    
    fig = px.histogram(
        df,
        x=column,
        nbins=15 if column != "Customer_Rating" else 5,
        marginal="box",
        title=f"Frequency Distribution of {column.replace('_', ' ')} (Interactive)",
        color_discrete_sequence=["#38bdf8"]
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        font=dict(color="#f8fafc")
    )
    return fig
