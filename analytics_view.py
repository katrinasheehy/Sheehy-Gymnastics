import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def create_context_chart(row, gymnast_name):
    is_boy = "Ansel" in gymnast_name
    x_min, x_max = (7.0, 10.0) if is_boy else (8.5, 10.0)
    fig = go.Figure()
    fig.add_trace(go.Bar(y=["Score"], x=[row['Session_Max'] - x_min], base=x_min, orientation='h', marker_color='#E0E0E0', hoverinfo='skip', width=0.4))
    fig.add_trace(go.Scatter(x=[row['Score']], y=["Score"], mode='markers+text', marker=dict(symbol='star', size=18, color='gold', line=dict(width=1.5, color='black')), text=[f"<b>{row['Score']:.3f}</b>"], textposition="top center"))
    fig.add_trace(go.Scatter(x=[row['Session_Median']], y=["Score"], mode='markers+text', marker=dict(symbol='line-ns-open', size=24, color='white', line=dict(width=3)), text=[f"{row['Session_Median']:.2f}"], textposition="bottom center"))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(l=10, r=10, t=30, b=20), height=130, xaxis=dict(range=[x_min, x_max], showgrid=False, dtick=0.5), yaxis=dict(showticklabels=False))
    return fig

def get_jsi_label(jsi):
    if jsi <= -0.15: return "🌬️ Significantly Stricter"
    if jsi <= -0.05: return "☁️ Slightly Stricter"
    if jsi >= 0.15: return "☀️ Significantly Looser"
    if jsi >= 0.05: return "🌤️ Slightly Looser"
    return "⚖️ Average Scoring"

def show_athlete_history(gymnast_name, selected_meet, theme_color):
    df_ctx = pd.read_csv("session_context_analytics.csv")
    meet_rows = df_ctx[(df_ctx['Gymnast'].str.contains(gymnast_name.split()[0], case=False)) & (df_ctx['Meet'] == selected_meet)]

    for _, row in meet_rows.iterrows():
        # Using a custom HTML layout for the "Left Label" design
        col_label, col_chart = st.columns([1, 4])
        
        with col_label:
            st.markdown(f"<div style='margin-top:45px; font-weight:bold; font-size:1.1rem;'>{row['Event']}</div>", unsafe_allow_html=True)
        
        with col_chart:
            st.plotly_chart(create_context_chart(row, gymnast_name), use_container_width=True, config={'staticPlot': True})
            
        # Small stats line underneath the chart
        st.markdown(f"""
            <div style='margin-top:-25px; margin-bottom:15px; font-size:0.85rem; color:#666;'>
                🏆 <b>Top {row['Percentile']:.0f}%</b> of {int(row['Count'])} athletes | 
                <b>Mood:</b> {get_jsi_label(row['JSI'])}
            </div>
        """, unsafe_allow_html=True)
