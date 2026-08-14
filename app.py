import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io

# Page Setup & Dark Theme CSS Styling
st.set_page_config(
    page_title="RM Performance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0b0e1e;
        color: #ffffff;
    }
    div[data-testid="metric-container"] {
        background-color: #161a35;
        border: 1px solid #282d54;
        padding: 15px;
        border-radius: 10px;
    }
    .kpi-card {
        background-color: #161a35;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #282d54;
        text-align: center;
    }
    .kpi-title { font-size: 13px; color: #a0a5c0; margin-bottom: 5px; font-weight: 600; }
    .kpi-value { font-size: 26px; font-weight: bold; color: #ffffff; }
    .kpi-sub { font-size: 12px; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# Helper function for dark layout styling on Plotly charts
def update_dark_layout(fig, title=""):
    fig.update_layout(
        title={'text': title, 'y': 0.9, 'x': 0.05, 'xanchor': 'left', 'yanchor': 'top'},
        paper_bgcolor='rgba(22, 26, 53, 1)',
        plot_bgcolor='rgba(22, 26, 53, 1)',
        font=dict(color="#e0e0e0", family="Sans-serif"),
        margin=dict(l=30, r=30, t=50, b=30),
        height=320
    )
    return fig

# Dashboard Title Banner
st.markdown("<h2 style='color: #ffffff; margin-bottom: 20px;'>RM Performance Analysis Dashboard</h2>", unsafe_allow_html=True)

# Sidebar: File Import & Filter Options
st.sidebar.header("📁 Data Import & Filters")
uploaded_file = st.sidebar.file_uploader("Upload RM Excel File", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception:
        df = pd.read_excel(uploaded_file, sheet_name=0)
else:
    # Default sample data containing Plan vs Actual metrics
    df = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'RM_Name': ['RM Alpha', 'RM Beta', 'RM Gamma', 'RM Delta', 'RM Epsilon', 'RM Zeta'],
        'Target': [100, 120, 110, 130, 125, 140],
        'Actual': [95, 115, 118, 122, 130, 145],
        'Deposit_Target': [500, 600, 550, 650, 620, 700],
        'Deposit_Actual': [480, 590, 570, 640, 650, 720],
        'CSAT': [85, 88, 90, 87, 92, 94],
        'Promoters': [67.7, 70.2, 65.4, 68.0, 72.1, 75.0]
    })

# RM Filter Selection
rm_list = ["All RMs"] + list(df['RM_Name'].unique()) if 'RM_Name' in df.columns else ["All RMs"]
selected_rm = st.sidebar.selectbox("Select Relationship Manager", rm_list)

filtered_df = df if selected_rm == "All RMs" else df[df['RM_Name'] == selected_rm]

# Excel Export Section
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Export Dashboard Data")

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    filtered_df.to_excel(writer, index=False, sheet_name='RM_Performance')

st.sidebar.download_button(
    label="Download Data as Excel",
    data=buffer.getvalue(),
    file_name=f"RM_Performance_{selected_rm.replace(' ', '_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Core Metric Calculations
total_target = filtered_df['Target'].sum() if 'Target' in filtered_df.columns else 0
total_actual = filtered_df['Actual'].sum() if 'Actual' in filtered_df.columns else 0
achievement_rate = (total_actual / total_target * 100) if total_target > 0 else 0
avg_csat = filtered_df['CSAT'].mean() if 'CSAT' in filtered_df.columns else 0

# Row 1: KPI Cards
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">TOTAL TARGET (PLAN)</div>
        <div class="kpi-value">{total_target:,.0f}</div>
        <div class="kpi-sub" style="color: #a0a5c0;">Assigned Goal</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    variance = total_actual - total_target
    color = "#4cd137" if variance >= 0 else "#e84118"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">ACTUAL ACHIEVED</div>
        <div class="kpi-value">{total_actual:,.0f}</div>
        <div class="kpi-sub" style="color: {color};">{"▲" if variance >= 0 else "▼"} {abs(variance):,.0f} Variance</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">ACHIEVEMENT RATE</div>
        <div class="kpi-value">{achievement_rate:.1f}%</div>
        <div class="kpi-sub" style="color: #00d2d3;">Plan vs Actual Ratio</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">CSAT SCORE</div>
        <div class="kpi-value">{avg_csat:.1f}%</div>
        <div class="kpi-sub" style="color: #54a0ff;">Customer Satisfaction</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Row 2: Performance Gauge Indicators
g1, g2, g3 = st.columns(3)

def create_gauge(value, title, color="#2e86de"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 14, 'color': '#ffffff'}},
        number={'suffix': "%", 'font': {'size': 24, 'color': '#ffffff'}},
        gauge={
            'axis': {'range': [0, 120], 'tickwidth': 1, 'tickcolor': "#555"},
            'bar': {'color': color},
            'bgcolor': "#10132b",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 60], 'color': '#20264d'},
                {'range': [60, 120], 'color': '#1a2042'}
            ],
        }
    ))
    return update_dark_layout(fig)

with g1:
    st.plotly_chart(create_gauge(achievement_rate, "Target Achievement Rate", "#00d2d3"), use_container_width=True)

with g2:
    csat_val = filtered_df['CSAT'].iloc[-1] if 'CSAT' in filtered_df.columns else 0
    st.plotly_chart(create_gauge(csat_val, "Customer Effort Score (CES)", "#ff9f43"), use_container_width=True)

with g3:
    nps_val = filtered_df['Promoters'].iloc[-1] if 'Promoters' in filtered_df.columns else 0
    st.plotly_chart(create_gauge(nps_val, "Net Performance Score (NPS)", "#54a0ff"), use_container_width=True)

# Row 3: Visual Analytics
c1, c2 = st.columns(2)

with c1:
    fig_bar = go.Figure()
    categories = filtered_df['RM_Name'] if 'RM_Name' in filtered_df.columns else filtered_df['Month']
    
    if 'Deposit_Target' in filtered_df.columns:
        fig_bar.add_trace(go.Bar(name='Deposit Target', x=categories, y=filtered_df['Deposit_Target'], marker_color='#282d54'))
    if 'Deposit_Actual' in filtered_df.columns:
        fig_bar.add_trace(go.Bar(name='Deposit Actual', x=categories, y=filtered_df['Deposit_Actual'], marker_color='#10ac84'))
    
    fig_bar.update_layout(barmode='group')
    update_dark_layout(fig_bar, "Deposit Target vs Actual")
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    fig_line = go.Figure()
    x_axis = filtered_df['Month'] if 'Month' in filtered_df.columns else range(len(filtered_df))
    
    if 'Actual' in filtered_df.columns:
        fig_line.add_trace(go.Scatter(x=x_axis, y=filtered_df['Actual'], mode='lines+markers', name='Actual', line=dict(color='#00d2d3', width=3)))
    if 'Target' in filtered_df.columns:
        fig_line.add_trace(go.Scatter(x=x_axis, y=filtered_df['Target'], mode='lines', name='Plan (Target)', line=dict(color='#ff6b6b', width=2, dash='dash')))
        
    update_dark_layout(fig_line, "Overall Achievement Trend")
    st.plotly_chart(fig_line, use_container_width=True)