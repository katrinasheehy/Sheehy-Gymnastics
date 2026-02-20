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
    # Scale markers: 7-10 for Boys, 8-10 for Girls
    is_boy = any(name in gymnast_name for name in ["Ansel"])
    x_min = 7.0 if is_boy else 8.0
    x_max = 10.0
    
    fig = go.Figure()
    
# Layer 1: Whole Level (Wide Light Gray Bar - The "Anchor")
    fig.add_trace(go.Bar(
        y=[0.23], x=[row['Level_Max'] - x_min], base=x_min,
        orientation='h', marker_color='#F0F0F0', hoverinfo='skip', 
        width=0.3
    ))
    
    # Layer 2: Age Division (Inner Slate Blue Bar - Centered)
    fig.add_trace(go.Bar(
        y=[0.25], x=[row['Div_Max'] - x_min], base=x_min,
        orientation='h', marker_color='#708090', hoverinfo='skip', 
        width=0.15 
    ))

    # --- FINAL CORRECTED LABELS ---
    # Top label: Lined up with the top of the nested bars
    fig.add_annotation(
        x=x_min, y=0.42, 
        text="Age Division", # The "Inner" specific pond
        showarrow=False, 
        font=dict(size=10, color="black", weight="bold"), 
        xanchor="left"
    )
    
    # Bottom label: Pinned to the very bottom as the foundation
    fig.add_annotation(
        x=x_min, y=0.08, 
        text="Whole Level", # The "Big" pond foundation
        showarrow=False, 
        font=dict(size=10, color="black"), 
        xanchor="left", yanchor="top"
    )

    
    # Layer 3: The Score (Gold Star) - Text moved higher to y=0.5
    fig.add_trace(go.Scatter(
        x=[row['Score']], y=[0.25], mode='markers+text',
        marker=dict(symbol='star', size=20, color='gold', line=dict(width=1.5, color='black')),
        text=[f"<b>{row['Score']:.3f}</b>"], 
        textposition="top center",
        textfont=dict(size=13)
    ))
    
    # Layer 4: Level Median (White Vertical Line)
    # Set size to 20 so it spans only the thickness of the Light Gray bar (0.3 width)
    fig.add_trace(go.Scatter(
        x=[row['Level_Median']], y=[0.25], mode='markers',
        marker=dict(
            symbol='line-ns-open', 
            size=20,          # Reduced from 26 to fit the 0.3 bar width
            color='white', 
            line=dict(width=3)
        ),
        hoverinfo='skip'
    ))

   
    
   # Bar Labels
    # Top label: Pinned to the top of the Whole Level bar
    fig.add_annotation(
        x=x_min, y=0.48, 
        text="Whole Level", 
        showarrow=False, 
        font=dict(size=10, color="black"), # Changed to black
        xanchor="left"
    )
    
    # Bottom label: Pinned to the bottom of the Age Division bar
    fig.add_annotation(
        x=x_min, y=0.175, 
        text="Age Division", 
        showarrow=False, 
        font=dict(size=10, color="black", weight="bold"), # Changed to black + Bold
        xanchor="left", yanchor="top"
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, margin=dict(l=0, r=5, t=40, b=30), height=140,
        xaxis=dict(
            range=[x_min, x_max + 0.05], 
            showgrid=False, 
            tickmode='linear', 
            tick0=x_min, 
            dtick=0.5, 
            side="bottom", 
            tickfont=dict(size=10)
        ),
        yaxis=dict(showticklabels=False, range=[-0.2, 0.8])
    )
    return fig

def show_athlete_history_v2(gymnast_name, selected_meet, theme_color):
    try:
        df_ctx = pd.read_csv("v2_session_context.csv")
        df_jsi = pd.read_csv("v2_judge_analytics.csv")
    except FileNotFoundError:
        st.error("V2 Data files not found.")
        return
    
    # Filter updated to EXCLUDE 'AA'
    meet_rows = df_ctx[
        (df_ctx['Gymnast'].str.contains(gymnast_name.split()[0], case=False)) & 
        (df_ctx['Meet'] == selected_meet) & 
        (df_ctx['Event'] != 'AA')
    ]
    
    for _, row in meet_rows.iterrows():
        jsi_match = df_jsi[(df_jsi['Meet'] == row['Meet']) & (df_jsi['Level'] == str(row['Level'])) & (df_jsi['Event'] == row['Event'])]
        
        if not jsi_match.empty:
            jsi_val, iqr_val = jsi_match.iloc[0]['JSI_Standard'], jsi_match.iloc[0]['IQR']
            profile_label = get_judge_profile(jsi_val, iqr_val)
        else:
            profile_label, jsi_val, iqr_val = "Pending", 0, 0

        c1, c2 = st.columns([1, 6])
        with c1:
            st.markdown(f"<div style='margin-top:50px; font-weight:bold; font-size:1rem;'>{row['Event']}</div>", unsafe_allow_html=True)
        with c2:
            st.plotly_chart(create_v2_context_chart(row, gymnast_name), use_container_width=True, config={'staticPlot': True})
        
        st.markdown(f"""
            <div style='margin-top:-25px; padding-top:10px; margin-bottom:20px; font-size:0.85rem; color:#888;'>
                🏆 <b>Top {row['Percentile']:.1f}%</b> of {int(row['Count'])} Level {row['Level']}s | 
                <b>Judge Profile:</b> {profile_label} (JSI: {jsi_val:.2f} | IQR: {iqr_val:.2f})
            </div>
        """, unsafe_allow_html=True)
