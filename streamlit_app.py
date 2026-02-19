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

# --- 1. Global CSS & Branded Elements ---
def inject_custom_css(color):
    st.markdown(f"""
        <style>
        /* Force Title to 1 line */
        h1 {{ white-space: nowrap; font-size: 1.6rem !important; overflow: hidden; }}
        
        /* Kill default Red Selection Bar */
        [data-testid="stTabSelectionData"] {{ display: none !important; }}
        
        /* Tab Text Color & Size */
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {{
            font-size: 24px !important;
            font-weight: bold;
            color: {color} !important;
        }}

        /* Meet Context Condensed Layout */
        .context-row {{
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }}
        .context-event-label {{
            min-width: 60px;
            font-weight: bold;
            font-size: 0.9rem;
            color: #444;
        }}
        .context-chart-area {{ flex-grow: 1; }}

        /* Table Highlighting */
        .pb-highlight {{
            background-color: {color}22; /* 22 is 13% opacity */
            font-weight: bold;
            border: 2px solid {color} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- 2. The Master Gymnast Function ---
def show_gymnast_tab(name, color, events, header_class):
    inject_custom_css(color)
    
    subset = df[df['Gymnast'].astype(str).str.contains(name, case=False, na=False)].copy()
    if subset.empty: return

    # A. Navigation (Descending Order, Most Recent Top)
    all_meets = sorted(subset['Meet'].unique(), key=lambda x: subset[subset['Meet']==x]['Date'].max(), reverse=True)
    selected_meet = st.selectbox("📅 Select Meet", all_meets, index=0, key=f"nav_{name}")
    latest = subset[subset['Meet'] == selected_meet].iloc[-1]
    
    # B. Side-by-Side Metrics (Transparent)
    aa_val = latest.get('AA', None)
    rank = latest.get('Meet_Rank', '')
    total = latest.get('Meet_Rank_Total', '')
    aa_display = f"{aa_val:.3f}" if pd.notna(aa_val) else "-"
    rank_display = f"{int(float(rank))} / {int(float(total))}" if pd.notna(rank) else "-"

    st.markdown(f"""
        <table style="width:100%; border:none; margin-top:10px;">
            <tr>
                <td style="width:50%; text-align:center; border:none;">
                    <div style="color:gray; font-size:12px;">All-Around (AA)</div>
                    <div style="font-size:32px; font-weight:bold; color:{color};">{aa_display}</div>
                </td>
                <td style="width:50%; text-align:center; border:none;">
                    <div style="color:gray; font-size:12px;">🏆 Meet Rank</div>
                    <div style="font-size:32px; font-weight:bold;">{rank_display}</div>
                </td>
            </tr>
        </table>
    """, unsafe_allow_html=True)

    # C. Score Table with PB Highlighting
    current_year = latest['Date'].year
    year_data = subset[subset['Date'].dt.year == current_year]
    
    score_row, rank_row, pb_row = [], [], []
    cols = list(events.keys()) + ["AA"]
    
    for col in cols:
        val = latest.get(col, 0)
        season_pb = year_data[col].max() if col in year_data.columns else 0
        
        # Formatting rows
        score_row.append(f"{val:.3f}")
        rank_val = latest.get(f"{col}_Rank" if col != "AA" else "Meet_Rank", "-")
        rank_row.append(str(rank_val).replace('.0', ''))
        pb_row.append(f"{season_pb:.3f}")

    table_df = pd.DataFrame([score_row, rank_row, pb_row], 
                            columns=cols, 
                            index=["Score", f"{latest.get('Division', 'Div')} Rank", "Season PB"])

    # Highlight Logic: If Score == PB, color the cell
    def highlight_pb(s):
        return ['background-color: ' + color + '44; font-weight: bold' if s.iloc[0] == s.iloc[2] else '' for _ in range(len(s))]

    st.table(table_df)

    # D. Condensed Context Cards
    st.markdown(f'<p style="font-size:1rem; font-weight:bold; margin-top:20px;">🎯 Judge Analysis</p>', unsafe_allow_html=True)
    show_athlete_history(name, selected_meet, color)

    # E. Trend Chart (Fixed Season Labels)
    st.divider()
    st.subheader("📈 Season Progress")
    is_boy = "Ansel" in name
    y_min, y_max, threshold = (47, 56, 52) if is_boy else (35, 40, 38)
    
    chart_data = subset[subset['Date'].dt.month.between(1, 4)].sort_values('Date').copy()
    chart_data['Meet_ID'] = chart_data['Date'].dt.strftime('%Y-%m-%d') + " " + chart_data['Meet']

    fig = go.Figure()
    for i, yr in enumerate(chart_data['Date'].dt.year.unique()):
        yr_sub = chart_data[chart_data['Date'].dt.year == yr]
        # Line
        fig.add_trace(go.Scatter(x=yr_sub['Meet_ID'], y=yr_sub['AA'], mode='lines+markers', line=dict(color=color, width=3), marker=dict(size=8, color=color)))
        # Season Label (Fixed: White font, transparent bg)
        fig.add_annotation(x=yr_sub.iloc[len(yr_sub)//2]['Meet_ID'], y=y_min + 0.4, text=f"<b>{yr} Season</b>", showarrow=False, font=dict(color="white"))
        # Shading
        fig.add_vrect(x0=yr_sub.iloc[0]['Meet_ID'], x1=yr_sub.iloc[-1]['Meet_ID'], fillcolor="rgba(100,100,100,0.1)", layer="below", line_width=0)

    # Stars
    stars = chart_data[chart_data['AA'] >= threshold]
    fig.add_trace(go.Scatter(x=stars['Meet_ID'], y=stars['AA'], mode='markers', marker=dict(symbol='star', size=14, color='gold', line=dict(color='black', width=1))))

    fig.update_layout(yaxis=dict(range=[y_min, y_max], dtick=1), xaxis=dict(tickangle=45, tickvals=chart_data['Meet_ID'], ticktext=chart_data['Meet']), height=500, margin=dict(b=100, t=10), dragmode=False, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

# --- 5. Tabs ---
events_girls = {"VT": "Vault", "UB": "Bars", "BB": "Beam", "FX": "Floor"}
events_boys = {"FX": "Floor", "PH": "Pommel", "SR": "Rings", "VT": "Vault", "PB": "P-Bars", "HB": "H-Bar"}
tab1, tab2, tab3 = st.tabs(["Annabelle", "Azalea", "Ansel"])
with tab1: show_gymnast_tab("Annabelle", "#FF69B4", events_girls, "annabelle-header")
with tab2: show_gymnast_tab("Azalea", "#9370DB", events_girls, "azalea-header")
with tab3: show_gymnast_tab("Ansel", "#008080", events_boys, "ansel-header")
