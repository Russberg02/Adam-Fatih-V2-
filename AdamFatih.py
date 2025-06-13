import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.lines import Line2D

# Configuration
st.set_page_config(
    layout="wide",
    page_title="FATIH - Industrial Fatigue Assessment",
    page_icon="⚙️"
)

# Black and white color palette with high contrast
BLACK = "#000000"
DARK_GRAY = "#333333"
MEDIUM_GRAY = "#666666"
LIGHT_GRAY = "#e0e0e0"
WHITE = "#FFFFFF"
ACCENT = "#212121"  # Slightly lighter than black for visual hierarchy

# Custom CSS for high-contrast black and white styling
st.markdown(f"""
<style>
    /* Main styling */
    .stApp {{
        background-color: {WHITE};
        color: {BLACK};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* Titles and headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {BLACK} !important;
        border-bottom: 2px solid {DARK_GRAY};
        padding-bottom: 0.3rem;
    }}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: {DARK_GRAY};
        color: {WHITE};
    }}
    
    .sidebar .sidebar-content {{
        background-color: {DARK_GRAY};
        color: {WHITE};
    }}
    
    /* Button styling */
    .stButton>button {{
        background-color: {BLACK};
        color: {WHITE};
        border-radius: 4px;
        border: none;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }}
    
    .stButton>button:hover {{
        background-color: {MEDIUM_GRAY};
        color: {WHITE};
    }}
    
    /* Card styling */
    .card {{
        background: {WHITE};
        border-radius: 5px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid {DARK_GRAY};
        border: 1px solid {LIGHT_GRAY};
    }}
    
    /* Status indicators */
    .safe {{
        color: {MEDIUM_GRAY};
        font-weight: bold;
    }}
    
    .unsafe {{
        color: {BLACK};
        font-weight: bold;
    }}
    
    /* Value display */
    .value-display {{
        font-size: 1.6rem;
        font-weight: bold;
        color: {BLACK};
    }}
    
    /* Section headers */
    .section-header {{
        background-color: {LIGHT_GRAY};
        color: {BLACK};
        padding: 10px 15px;
        border-radius: 4px;
        margin-top: 20px;
        border-left: 4px solid {BLACK};
    }}
    
    /* Material design elements */
    .material-card {{
        background: {WHITE};
        border: 1px solid {LIGHT_GRAY};
        border-radius: 4px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }}
    
    /* Progress bars */
    .progress-container {{
        height: 8px;
        background-color: {LIGHT_GRAY};
        border-radius: 4px;
        margin: 10px 0;
        overflow: hidden;
    }}
    
    .progress-bar {{
        height: 100%;
        background-color: {DARK_GRAY};
    }}
    
    /* Table styling */
    table {{
        border: 1px solid {LIGHT_GRAY} !important;
    }}
    
    tr {{
        border-bottom: 1px solid {LIGHT_GRAY} !important;
    }}
    
    td {{
        border: none !important;
    }}
    
    /* Expander styling */
    .stExpander {{
        border: 1px solid {LIGHT_GRAY} !important;
        border-radius: 4px;
        margin-bottom: 10px;
    }}
    
    .st-emotion-cache-1c7k2aw {{
        border-color: {LIGHT_GRAY} !important;
    }}
    
    /* Plot styling */
    .st-emotion-cache-1v0mbdj {{
        border: 1px solid {LIGHT_GRAY} !important;
        border-radius: 4px;
        padding: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# App header with high contrast theme
st.markdown(f"""
<div style="background-color:{DARK_GRAY}; padding:20px; border-radius:5px; margin-bottom:20px;">
    <h1 style="color:{WHITE}; margin:0;">⚙️ FATIH - Industrial Fatigue Assessment Tool</h1>
    <p style="color:#b0b0b0;">Pipeline Integrity Management System for Energy Sector</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with high contrast scheme
with st.sidebar:
    st.markdown(f"""
    <div style="background-color:{BLACK}; padding:10px; border-radius:4px; margin-bottom:15px;">
        <h3 style="color:{WHITE}; margin:0;">Pipeline Parameters</h3>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📏 Dimensional Parameters", expanded=True):
        inputs = {
            'pipe_thickness': st.number_input('Pipe Thickness, t (mm)', min_value=0.1, value=10.0),
            'pipe_diameter': st.number_input('Pipe Diameter, D (mm)', min_value=0.1, value=200.0),
            'pipe_length': st.number_input('Pipe Length, L (mm)', min_value=0.1, value=1000.0),
            'corrosion_length': st.number_input('Corrosion Length, Lc (mm)', min_value=0.0, value=50.0),
            'corrosion_depth': st.number_input('Corrosion Depth, Dc (mm)', min_value=0.0, max_value=10.0, value=2.0)
        }
    
    with st.expander("🧱 Material Properties", expanded=True):
        inputs['yield_stress'] = st.number_input('Yield Stress, Sy (MPa)', min_value=0.1, value=300.0)
        inputs['uts'] = st.number_input('Ultimate Tensile Strength, UTS (MPa)', min_value=0.1, value=400.0)
    
    with st.expander("📊 Operating Conditions", expanded=True):
        inputs['max_pressure'] = st.slider('Max Operating Pressure (MPa)', 0, 50, 10)
        inputs['min_pressure'] = st.slider('Min Operating Pressure (MPa)', 0, 50, 5)
    
    st.markdown("---")
    st.markdown(f"""
    <div style="background-color:{BLACK}; padding:10px; border-radius:4px; margin-top:15px;">
        <h4 style="color:{WHITE}; margin:0;">Safety Indicators</h4>
        <p style="color:#b0b0b0; margin:0;">✅ Safe: Value ≤ 1<br>❌ Unsafe: Value > 1</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button('Run Analysis', use_container_width=True, type="primary"):
        st.session_state.run_analysis = True
    if st.button('Reset Values', use_container_width=True):
        st.session_state.run_analysis = False

# Image and intro section
st.subheader('Pipeline Configuration')
col1, col2 = st.columns([1, 2])
with col1:
    st.image("https://www.researchgate.net/profile/Changqing-Gong/publication/313456917/figure/fig1/AS:573308992266241@1513698923813/Schematic-illustration-of-the-geometry-of-a-typical-corrosion-defect.png", 
             caption="Fig. 1: Corrosion defect geometry")
with col2:
    st.markdown(f"""
    <div class="material-card">
        <h4 style="border-bottom: 1px solid {LIGHT_GRAY}; padding-bottom: 5px;">Assessment Protocol</h4>
        <ol>
            <li>Enter pipeline dimensions and material properties</li>
            <li>Specify operating pressure range</li>
            <li>Click "Run Analysis" to perform assessment</li>
            <li>Review burst pressure calculations</li>
            <li>Analyze stress and fatigue results</li>
            <li>Check safety status for all criteria</li>
        </ol>
        <div class="progress-container">
            <div class="progress-bar" style="width: {'50%' if st.session_state.get('run_analysis', False) else '10%'};"></div>
        </div>
        <p style="text-align: right; margin:0;">Status: {'Analysis Complete' if st.session_state.get('run_analysis', False) else 'Ready for Input'}</p>
    </div>
    """, unsafe_allow_html=True)

# Calculations (same as before)

# Main analysis section (same as before)

# References and footer (same as before)
