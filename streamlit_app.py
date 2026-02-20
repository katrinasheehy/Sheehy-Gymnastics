#version 2
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from analytics_view import show_athlete_history_v2

st.set_page_config(page_title="Sheehy All-Around V2", layout="centered")

# Check if live scores exist and display them
if os.path.exists("live_scores.csv"):
    st.markdown("### 🔴 Live Results (Saturday)")
    live_df = pd.read_csv("live_scores.csv")
    # Show only the last 3 entries to keep it compact
    st.table(live_df.tail(3)[["Gymnast", "Event", "Score"]])

@st.cache_data
def load_data():
    df = pd.read_csv("v2_cleaned_gymnastics.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# Global CSS
st.markdown("""
    <style>
    h1 { white-space: nowrap; font-size: 1.6rem !important; overflow: hidden; margin-bottom: 5px; }
    [data-testid="stTabSelectionData"] { display: none !important; }
    hr { display: none !important; }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 24px !important; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def show_gymnast_tab(name, color, events):
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
    
    # Top Metrics: Meet Rank
    aa_val = latest.get('AA', 0)
    m_rank = latest.get('Meet_Rank', '-')
    m_total = latest.get('Meet_Rank_Total', '-')
    rank_display = f"{int(float(m_rank))} / {int(float(m_total))}" if str(m_rank) != '-' else "-"

    st.markdown(f"""
        <table style="width:100%; border:none; margin-top:10px;">
            <tr>
                <td style="width:50%; text-align:center; border:none;">
                    <div style="color:gray; font-size:12px;">All-Around (AA)</div>
                    <div style="font-size:32px; font-weight:bold; color:{color};">{aa_val:.3f}</div>
                </td>
                <td style="width:50%; text-align:center; border:none;">
                    <div style="color:gray; font-size:12px;">🏆 Meet Rank</div>
                    <div style="font-size:32px; font-weight:bold;">{rank_display}</div>
                </td>
            </tr>
        </table>
    """, unsafe_allow_html=True)

    # Score Table: Division Rank & PB Highlights
    current_year = latest['Date'].year
    year_data = subset[subset['Date'].dt.year == current_year]
    cols = list(events.keys()) + ["AA"]
    score_row, rank_row, pb_row = [], [], []
    
    for c in cols:
        val = latest.get(c, 0)
        s_pb = year_data[c].max() if c in year_data.columns else 0
        score_row.append(val)
        # Pull Division Rank: AA_Rank for the AA column
        r_val = latest.get(f"{c}_Rank" if c != "AA" else "AA_Rank", "-")
        rank_row.append(str(r_val).replace('.0', ''))
        pb_row.append(s_pb)

    table_df = pd.DataFrame([score_row, rank_row, pb_row], columns=cols, 
                            index=["Score", f"{latest.get('Division', 'Div')} Rank", "Season PB"])

    def highlight_pb(data):
        attr = f'background-color: {color}; color: white; font-weight: bold;'
        is_pb = data.loc['Score'] == data.loc['Season PB']
        return pd.DataFrame([[attr if is_pb[col] else '' for col in data.columns],
                             ['' for _ in data.columns],
                             ['' for _ in data.columns]], index=data.index, columns=data.columns)

    st.dataframe(table_df.style.apply(highlight_pb, axis=None).format(subset=(["Score", "Season PB"], slice(None)), formatter="{:.3f}"), use_container_width=True)

    st.markdown(f'<p style="font-size:1.1rem; font-weight:bold; margin-top:20px;">🎯 Event Analysis</p>', unsafe_allow_html=True)
    show_athlete_history_v2(name, selected_meet, color)

    # Trend Chart
    st.markdown(f'<p style="font-size:1.1rem; font-weight:bold; margin-top:20px;">📈 Season Progress</p>', unsafe_allow_html=True)
    is_boy = "Ansel" in name
    y_min, y_max, threshold = (47, 56, 52) if is_boy else (35, 40, 38)
    chart_data = subset[subset['Date'].dt.month.between(1, 4)].sort_values('Date').copy()
    chart_data['Meet_ID'] = chart_data['Date'].dt.strftime('%Y-%m-%d') + " " + chart_data['Meet']

    fig = go.Figure()
    for yr in chart_data['Date'].dt.year.unique():
        yr_sub = chart_data[chart_data['Date'].dt.year == yr]
        fig.add_vrect(x0=yr_sub.iloc[0]['Meet_ID'], x1=yr_sub.iloc[-1]['Meet_ID'], fillcolor="rgba(100,100,100,0.1)", layer="below", line_width=0)
        fig.add_annotation(x=yr_sub.iloc[len(yr_sub)//2]['Meet_ID'], y=y_min + 0.4, text=f"<b>{yr} Season</b>", showarrow=False, font=dict(color="white"))
        fig.add_trace(go.Scatter(x=yr_sub['Meet_ID'], y=yr_sub['AA'], mode='lines+markers', line=dict(color=color, width=3), marker=dict(size=8, color=color), showlegend=False))

    fig.add_hline(y=threshold, line_dash="dash", line_color="rgba(0,0,0,0.2)", line_width=2)
    
    pb_indices = chart_data.groupby(chart_data['Date'].dt.year)['AA'].idxmax()
    for idx in pb_indices:
        p = chart_data.loc[idx]
        fig.add_annotation(x=p['Meet_ID'], y=p['AA'], text=f"⭐ <b>PB: {p['AA']:.3f}</b>", showarrow=True, arrowhead=2, ay=-40, font=dict(color="white"), bgcolor=color, borderpad=4)

    fig.update_layout(yaxis=dict(range=[y_min, y_max], dtick=1), xaxis=dict(tickangle=45, tickvals=chart_data['Meet_ID'], ticktext=chart_data['Meet']), height=480, margin=dict(b=110, t=10), dragmode=False, template="plotly_white", showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

# Main Content
st.title("🤸 Sheehy All-Around")
events_girls = {"VT": "Vault", "UB": "Bars", "BB": "Beam", "FX": "Floor"}
events_boys = {"FX": "Floor", "PH": "Pommel", "SR": "Rings", "VT": "Vault", "PB": "P-Bars", "HB": "H-Bar"}
tab1, tab2, tab3 = st.tabs(["Annabelle", "Azalea", "Ansel"])
with tab1: show_gymnast_tab("Annabelle", "#FF69B4", events_girls)
with tab2: show_gymnast_tab("Azalea", "#9370DB", events_girls)
with tab3: show_gymnast_tab("Ansel", "#008080", events_boys)


import os

# --- Saturday Live Score Entry (Wine Country) ---
with st.sidebar:
    st.markdown("---")
    # Using a checkbox to keep the sidebar clean when not in use
    if st.checkbox("🔑 Enter Live Scores"):
        st.info("Entering scores for the Wine Country Meet.")
        
        with st.form("live_entry_form"):
            gymnast = st.selectbox("Gymnast", ["Annabelle", "Azalea", "Ansel"])
            event = st.selectbox("Event", ["VT", "UB", "BB", "FX", "PH", "SR", "PB", "HB"])
            score = st.number_input("Score", min_value=0.0, max_value=10.0, step=0.025, format="%.3f")
            
            # Simple password to prevent accidental clicks
            pwd = st.text_input("Admin Password", type="password")
            
            if st.form_submit_button("Submit Score"):
                if pwd == "bayshore":  # You can change this to any password you like
                    # Prepare the data
                    new_score = pd.DataFrame([[
                        pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                        gymnast, 
                        event, 
                        score,
                        "Wine Country 2026"
                    ]], columns=["Timestamp", "Gymnast", "Event", "Score", "Meet"])
                    
                    # Save to CSV (appends if file exists, creates if not)
                    file_name = "live_scores.csv"
                    new_score.to_csv(file_name, mode='a', header=not os.path.exists(file_name), index=False)
                    
                    st.success(f"Successfully saved {score} for {gymnast} on {event}!")
                else:
                    st.error("Incorrect password.")
