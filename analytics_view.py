#version 2 with nested level and division bars and updated JSI text based on strictness and consistency

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def get_judge_profile(jsi, iqr):
    # Categorizes judge based on strictness and consistency
    if jsi < -0.10:
        return "Fair but Tough" if iqr < 0.50 else "Strict & Unpredictable"
    elif jsi > 0.10:
        return "Generous but Precise" if iqr < 0.50 else "Generous but Erratic"
    else:
        return "Textbook Judging" if iqr < 0.50 else "Average but Erratic"

def create_v2_context_chart(row, gymnast_name):
    is_boy = any(name in gymnast_name for name in ["Ansel"])
    x_min, x_max = (7.0, 10.0) if is_boy else (8.5, 10.0)
    
    fig = go.Figure()
    
    # Layer 1: LEVEL Range (Wide Light Gray Bar)
    fig.add_trace(go.Bar(
        y=["Score"], x=[row['Level_Max'] - x_min], base=x_min,
        orientation='h', marker_color='#F0F0F0', hoverinfo='skip', width=0.6
    ))
    
    # Layer 2: DIVISION Range (Inner Darker Gray Bar)
    fig.add_trace(go.Bar(
        y=["Score"], x=[row['Div_Max'] - x_min], base=x_min,
        orientation='h', marker_color='#D0D0D0', hoverinfo='skip', width=0.3
    ))
    
    # Layer 3: The Score (Gold Star)
    fig.add_trace(go.Scatter(
        x=[row['Score']], y=["Score"], mode='markers+text',
        marker=dict(symbol='star', size=20, color='gold', line=dict(width=1.5, color='black')),
        text=[f"<b>{row['Score']:.3f}</b>"], textposition="top center"
    ))
    
    # Layer 4: Level Median (White Vertical Line)
    fig.add_trace(go.Scatter(
        x=[row['Level_Median']], y=["Score"], mode='markers',
        marker=dict(symbol='line-ns-open', size=24, color='white', line=dict(width=3))
        text=[f"<b>{row['Level_Median']:.3f}</b>"], textposition="top center"
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, margin=dict(l=0, r=0, t=30, b=25), height=110,
        xaxis=dict(range=[x_min, x_max + 0.05], showgrid=False, tickmode='linear', tick0=x_min, dtick=0.5, side="bottom", tickfont=dict(size=10)),
        yaxis=dict(showticklabels=False)
    )
    return fig

def show_athlete_history_v2(gymnast_name, selected_meet, theme_color):
    try:
        df_ctx = pd.read_csv("v2_session_context.csv")
        df_jsi = pd.read_csv("v2_judge_analytics.csv")
    except FileNotFoundError:
        st.error("V2 Data files not found. Ensure v2_session_context.csv and v2_judge_analytics.csv exist.")
        return
    
    # Filter for the specific gymnast and meet
    meet_rows = df_ctx[(df_ctx['Gymnast'].str.contains(gymnast_name.split()[0], case=False)) & (df_ctx['Meet'] == selected_meet)]
    
    for _, row in meet_rows.iterrows():
        # Look up JSI and IQR for this specific event
        jsi_match = df_jsi[(df_jsi['Meet'] == row['Meet']) & (df_jsi['Level'] == str(row['Level'])) & (df_jsi['Event'] == row['Event'])]
        
        if not jsi_match.empty:
            jsi_val = jsi_match.iloc[0]['JSI_Standard']
            iqr_val = jsi_match.iloc[0]['IQR']
            profile_label = get_judge_profile(jsi_val, iqr_val)
        else:
            profile_label = "Pending Data"
            jsi_val, iqr_val = 0, 0

        c1, c2 = st.columns([1, 6])
        with c1:
            st.markdown(f"<div style='margin-top:40px; font-weight:bold; font-size:1rem;'>{row['Event']}</div>", unsafe_allow_html=True)
        with c2:
            st.plotly_chart(create_v2_context_chart(row, gymnast_name), use_container_width=True, config={'staticPlot': True})
        
        st.markdown(f"""
            <div style='margin-top:-15px; padding-top:10px; margin-bottom:15px; font-size:0.8rem; color:#888;'>
                🏆 <b>Top {row['Percentile']:.1f}%</b> of {int(row['Count'])} Level {row['Level']}s | 
                👨‍⚖️ <b>Judge Profile:</b> {profile_label} (JSI: {jsi_val:.2f} | IQR: {iqr_val:.2f})
            </div>
        """, unsafe_allow_html=True)
