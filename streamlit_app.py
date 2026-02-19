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

# --- 3. Persistent App-Wide CSS (Sticky Tabs) ---
st.markdown("""
    <style>
    h1 { white-space: nowrap; font-size: 1.6rem !important; overflow: hidden; margin-bottom: 5px; }
    
    /* Sticky Header Logic */
    div[data-testid="stTabs"] {
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 999;
        padding-top: 10px;
    }

    [data-testid="stTabSelectionData"] { display: none !important; }
    hr { display: none !important; }
    
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 24px !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. The Master Gymnast Function ---
def show_gymnast_tab(name, color, events):
    # Dynamic CSS for child colors
    st.markdown(f"""
        <style>
        div[data-baseweb="select"] > div {{ border-color: {color} !important; }}
        .stTabs [data-baseweb="tab"]:nth-child(n)[aria-selected="true"] p {{ color: {color} !important; }}
        .stTabs [data-baseweb="tab"]:nth-child(n)[aria-selected="true"] {{ border-bottom: 4px solid {color} !important; }}
        </style>
    """, unsafe_allow_html=True)

    subset = df[df['Gymnast'].astype(str).str.contains(name, case=False, na=False)].copy()
    if subset.empty: return

    all_meets = sorted(subset['Meet'].unique(), key=lambda x: subset[subset['Meet']==x]['Date'].max(), reverse=True)
    selected_meet = st.selectbox("📅 Select Meet", all_meets, index=0, key=f"nav_{name}")
    latest = subset[subset['Meet'] == selected_meet].iloc[-1]
    
    # B. Side-by-Side Metrics (Pulls from AA_Rank for the Division)
    aa_val = latest.get('AA', 0)
    # Pulling AA_Rank which represents the Rank within the Division
    aa_div_rank = latest.get('AA_Rank', latest.get('Meet_Rank', '-'))
    total_in_div = latest.get('Meet_Rank_Total', '-')
    
    rank_display = f"{int(float(aa_div_rank))} / {int(float(total_in_div))}" if str(aa_div_rank) != '-' else "-"

    st.markdown(f"""
        <table style="width:100%; border:none; margin-top:10px;">
            <tr>
                <td style="width:50%; text-align:center; border:none;">
                    <div style="color:gray; font-size:12px;">All-Around (AA)</div>
                    <div style="font-size:32px; font-weight:bold; color:{color};">{aa_val:.3f}</div>
                </td>
                <td style="width:50%; text-align:center; border:none;">
                    <div style="color:gray; font-size:12px;">🏆 Division Rank</div>
                    <div style="font-size:32px; font-weight:bold;">{rank_display}</div>
                </td>
            </tr>
        </table>
    """, unsafe_allow_html=True)

    # C. Score Table with Correct Division Ranks
    current_year = latest['Date'].year
    year_data = subset[subset['Date'].dt.year == current_year]
    cols = list(events.keys()) + ["AA"]
    score_row, rank_row, pb_row = [], [], []
    
    for c in cols:
        val = latest.get(c, 0)
        s_pb = year_data[c].max() if c in year_data.columns else 0
        score_row.append(f"{val:.3f}")
        
        # Pull Rank: Event_Rank for events, AA_Rank for the AA column
        r_val = latest.get(f"{c}_Rank" if c != "AA" else "AA_Rank", latest.get("Meet_Rank", "-"))
        rank_row.append(str(r_val).replace('.0', ''))
        pb_row.append(f"{s_pb:.3f}")

    table_df = pd.DataFrame([score_row, rank_row, pb_row], columns=cols, 
                            index=["Score", f"{latest.get('Division', 'Div')} Rank", "Season PB"])
    st.table(table_df)

    # D. Condensed Event Analysis
    st.markdown(f'<p style="font-size:1.1rem; font-weight:bold; margin-top:20px;">🎯 Event Analysis</p>', unsafe_allow_html=True)
    show_athlete_history(name, selected_meet, color)

    # E. Trend Chart
    st.markdown(f'<p style="font-size:1.1rem; font-weight:bold; margin-top:20px;">📈 Season Progress</p>', unsafe_allow_html=True)
    is_boy = "Ansel" in name
    y_min, y_max, threshold = (47, 56, 52) if is_boy else (35, 40, 38)
    
    chart_data = subset[subset['Date'].dt.month.between(1, 4)].sort_values('Date').copy()
    chart_data['Meet_ID'] = chart_data['Date'].dt.strftime('%Y-%m-%d') + " " + chart_data['Meet']

    fig = go.Figure()
    for i, yr in enumerate(chart_data['Date'].dt.year.unique()):
        yr_sub = chart_data[chart_data['Date'].dt.year == yr]
        fig.add_vrect(x0=yr_sub.iloc[0]['Meet_ID'], x1=yr_sub.iloc[-1]['Meet_ID'], fillcolor="rgba(100,100,100,0.1)", layer="below", line_width=0)
        fig.add_annotation(x=yr_sub.iloc[len(yr_sub)//2]['Meet_ID'], y=y_min + 0.4, text=f"<b>{yr} Season</b>", showarrow=False, font=dict(color="white"))
        fig.add_trace(go.Scatter(x=yr_sub['Meet_ID'], y=yr_sub['AA'], mode='lines+markers', line=dict(color=color, width=3), marker=dict(size=8, color=color), showlegend=False))

    fig.add_hline(y=threshold, line_dash="dash", line_color="rgba(0,0,0,0.2)", line_width=2)
    stars = chart_data[chart_data['AA'] >= threshold]
    if not stars.empty:
        fig.add_trace(go.Scatter(x=stars['Meet_ID'], y=stars['AA'], mode='markers', marker=dict(symbol='star', size=14, color='gold', line=dict(color='black', width=1)), showlegend=False))

    pb_indices = chart_data.groupby(chart_data['Date'].dt.year)['AA'].idxmax()
    for idx in pb_indices:
        p = chart_data.loc[idx]
        fig.add_annotation(x=p['Meet_ID'], y=p['AA'], text=f"⭐ <b>PB: {p['AA']:.3f}</b>", showarrow=True, arrowhead=2, ay=-40, font=dict(color="white"), bgcolor=color, borderpad=4)

    fig.update_layout(yaxis=dict(range=[y_min, y_max], dtick=1), xaxis=dict(tickangle=45, tickvals=chart_data['Meet_ID'], ticktext=chart_data['Meet']), height=480, margin=dict(b=110, t=10), dragmode=False, template="plotly_white", showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

# --- 5. Main Execution ---
st.title("🤸 Sheehy All-Around")
events_girls = {"VT": "Vault", "UB": "Bars", "BB": "Beam", "FX": "Floor"}
events_boys = {"FX": "Floor", "PH": "Pommel", "SR": "Rings", "VT": "Vault", "PB": "P-Bars", "HB": "H-Bar"}
tab1, tab2, tab3 = st.tabs(["Annabelle", "Azalea", "Ansel"])
with tab1: show_gymnast_tab("Annabelle", "#FF69B4", events_girls)
with tab2: show_gymnast_tab("Azalea", "#9370DB", events_girls)
with tab3: show_gymnast_tab("Ansel", "#008080", events_boys)
    
