import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def create_context_chart(row, gymnast_name):
    is_boy = "Ansel" in gymnast_name
    x_min, x_max = (7.0, 10.0) if is_boy else (8.5, 10.0)
    fig = go.Figure()
    
    # Layer 1: Session Range
    fig.add_trace(go.Bar(y=["Score"], x=[row['Session_Max'] - x_min], base=x_min, orientation='h', marker_color='#E0E0E0', hoverinfo='skip', width=0.4))
    
    # Layer 2: The Score
    fig.add_trace(go.Scatter(x=[row['Score']], y=["Score"], mode='markers+text', marker=dict(symbol='star', size=18, color='gold', line=dict(width=1.5, color='black')), text=[f"<b>{row['Score']:.3f}</b>"], textposition="top center"))
    
    # Layer 3: The Median
    fig.add_trace(go.Scatter(x=[row['Session_Median']], y=["Score"], mode='markers+text', marker=dict(symbol='line-ns-open', size=24, color='white', line=dict(width=3)), text=[f"{row['Session_Median']:.2f}"], textposition="bottom center"))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        showlegend=False, 
        margin=dict(l=0, r=0, t=25, b=25), # Increased bottom margin to make space for labels
        height=110, 
        xaxis=dict(range=[x_min, x_max], showgrid=False, dtick=0.5, side="bottom", tickfont=dict(size=10)),
        yaxis=dict(showticklabels=False)
    )
    return fig

def get_jsi_label(jsi):
    if jsi <= -0.15: return "🌬️ Significantly Stricter"
    if jsi <= -0.05: return "☁️ Slightly Stricter"
    if jsi >= 0.15: return "☀️ Significantly Looser"
    if jsi >= 0.05: return "🌤️ Slightly Looser"
    return "⚖️ Average Scoring"

def show_athlete_history(gymnast_name, selected_meet, color):
    try:
        df_ctx = pd.read_csv("session_context_analytics.csv")
    except FileNotFoundError: return
    
    meet_rows = df_ctx[(df_ctx['Gymnast'].str.contains(gymnast_name.split()[0], case=False)) & (df_ctx['Meet'] == selected_meet)]
    
    for _, row in meet_rows.iterrows():
        c1, c2 = st.columns([1, 6])
        with c1:
            st.markdown(f"<div style='margin-top:35px; font-weight:bold; font-size:1rem;'>{row['Event']}</div>", unsafe_allow_html=True)
        with c2:
            st.plotly_chart(create_context_chart(row, gymnast_name), use_container_width=True, config={'staticPlot': True})
        
        # Added padding-top: 10px to push this line down away from the graph axis
        mood_label = get_jsi_label(row['JSI'])
        st.markdown(f"""
            <div style='margin-top:-15px; padding-top:10px; margin-bottom:12px; font-size:0.8rem; color:#888;'>
                🏆 <b>Top {row['Percentile']:.0f}%</b> of {int(row['Count'])} gymnasts | <b>Judge's Mood:</b> {mood_label} ({row['JSI']:.2f})
            </div>
        """, unsafe_allow_html=True)
