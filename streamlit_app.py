#the main dashboard and layout

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from analytics_view import show_athlete_history

# --- 1. Page Config ---
st.set_page_config(page_title="Sheehy All-Around", layout="centered")

# --- 2. Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_gymnastics.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# --- 3. App Header ---
st.title("🤸 Sheehy All-Around")

# --- 4. The Main Gymnast Function ---
def show_gymnast_tab(name, color, events, header_class):
    # CSS Injection for big tabs, no red line, and side-by-side metrics
    st.markdown(f"""
        <style>
        [data-testid="stTabSelectionData"] {{ display: none !important; }}
        div[data-baseweb="select"] > div {{ border-color: {color} !important; }}
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {{
            font-size: 26px !important;
            font-weight: bold;
        }}
        .context-header {{ font-size: 1.2rem !important; margin-top: 20px; font-weight: bold; }}
        .metric-label {{ color: gray; font-size: 14px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; }}
        </style>
    """, unsafe_allow_html=True)

    subset = df[df['Gymnast'].astype(str).str.contains(name, case=False, na=False)].copy()
    if subset.empty: return

    # A. Navigation
    all_meets = list(subset['Meet'].unique())[::-1]
    selected_meet = st.selectbox("📅 Select Meet History", all_meets, index=0, key=f"nav_{name}")
    latest = subset[subset['Meet'] == selected_meet].iloc[-1]
    
    # B. Metrics (Transparent HTML Table forces side-by-side)
    aa_val = latest.get('AA', None)
    rank = latest.get('Meet_Rank', '')
    total = latest.get('Meet_Rank_Total', '')
    aa_display = f"{aa_val:.3f}" if pd.notna(aa_val) else "-"
    rank_display = f"{int(float(rank))} / {int(float(total))}" if pd.notna(rank) else "-"

    st.markdown(f"""
        <table style="width:100%; border:none; border-collapse:collapse; margin-top:10px;">
            <tr>
                <td style="width:50%; text-align:center; border:none;">
                    <div class="metric-label">All-Around (AA)</div>
                    <div class="metric-value" style="color:{color};">{aa_display}</div>
                </td>
                <td style="width:50%; text-align:center; border:none;">
                    <div class="metric-label">🏆 Meet Rank</div>
                    <div class="metric-value">{rank_display}</div>
                </td>
            </tr>
        </table>
    """, unsafe_allow_html=True)

    # C. Score Table
    score_row, rank_row = [], []
    for evt in events.keys():
        val = latest.get(evt, None)
        score_row.append(f"{val:.3f}" if pd.notna(val) and val != 0 else "-")
        r_val = latest.get(f"{evt}_Rank", "-")
        rank_row.append(f"{str(r_val).replace('.0', '')}" if pd.notna(r_val) and str(r_val) != "0" else "-")
    score_row.append(f"{aa_val:.3f}"); rank_row.append(f"{str(latest.get('Meet_Rank', '-')).replace('.0', '')}")
    st.table(pd.DataFrame([score_row, rank_row], columns=list(events.keys()) + ["AA"], index=["Score", f"{latest.get('Division', 'Div')} Rank"]))

    # D. Context Cards
    st.markdown('<p class="context-header">🎯 Meet Context & Judge Analysis</p>', unsafe_allow_html=True)
    show_athlete_history(name, selected_meet)

    # E. Trend Chart (Shaded Seasons)
    st.divider()
    st.subheader("📈 Season Progress")
    is_boy = "Ansel" in name
    y_min, y_max, threshold = (47, 56, 52) if is_boy else (35, 40, 38)
    chart_data = subset.dropna(subset=['AA']).copy()
    chart_data['Month_Num'] = chart_data['Date'].dt.month
    chart_data = chart_data[chart_data['Month_Num'].between(1, 4)].copy()
    chart_data = chart_data.sort_values('Date')
    chart_data['Meet_ID'] = chart_data['Date'].dt.strftime('%Y-%m-%d') + " " + chart_data['Meet']
    chart_data['Year'] = chart_data['Date'].dt.year

    fig = go.Figure()
    shade_colors = ["rgba(200, 200, 200, 0.2)", "rgba(150, 150, 150, 0.1)"]
    for i, yr in enumerate(chart_data['Year'].unique()):
        yr_subset = chart_data[chart_data['Year'] == yr]
        fig.add_vrect(x0=yr_subset.iloc[0]['Meet_ID'], x1=yr_subset.iloc[-1]['Meet_ID'], fillcolor=shade_colors[i % 2], opacity=0.5, layer="below", line_width=0)
        fig.add_annotation(x=yr_subset.iloc[len(yr_subset)//2]['Meet_ID'], y=y_min + 0.5, text=f"<b>{yr} Season</b>", showarrow=False, bgcolor="white")
        fig.add_trace(go.Scatter(x=yr_subset['Meet_ID'], y=yr_subset['AA'], mode='lines+markers', line=dict(color=color, width=3), marker=dict(size=8, color=color)))
    
    stars = chart_data[chart_data['AA'] >= threshold]
    if not stars.empty:
        fig.add_trace(go.Scatter(x=stars['Meet_ID'], y=stars['AA'], mode='markers', marker=dict(symbol='star', size=14, color='gold', line=dict(width=1, color='black'))))
    
    pb_data = chart_data.loc[chart_data.groupby('Year')['AA'].idxmax()]
    for _, pb in pb_data.iterrows():
        fig.add_annotation(x=pb['Meet_ID'], y=pb['AA'], text=f"⭐ <b>PB: {pb['AA']:.3f}</b>", showarrow=True, arrowhead=2, ay=-40, font=dict(color="white"), bgcolor=color)
    
    fig.update_layout(yaxis=dict(range=[y_min, y_max], title="AA Score", dtick=1), xaxis=dict(tickangle=45, tickvals=chart_data['Meet_ID'], ticktext=chart_data['Meet']), showlegend=False, height=550, margin=dict(b=120), dragmode=False, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

# --- 5. Tabs ---
events_girls = {"VT": "Vault", "UB": "Bars", "BB": "Beam", "FX": "Floor"}
events_boys = {"FX": "Floor", "PH": "Pommel", "SR": "Rings", "VT": "Vault", "PB": "P-Bars", "HB": "H-Bar"}
tab1, tab2, tab3 = st.tabs(["Annabelle", "Azalea", "Ansel"])
with tab1: show_gymnast_tab("Annabelle", "#FF69B4", events_girls, "annabelle-header")
with tab2: show_gymnast_tab("Azalea", "#9370DB", events_girls, "azalea-header")
with tab3: show_gymnast_tab("Ansel", "#008080", events_boys, "ansel-header")
