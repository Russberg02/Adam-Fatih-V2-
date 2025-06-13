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

# Theme-aware color palette
def get_colors():
    is_dark = st.get_option("theme.base") == "dark"
    return {
        'primary': '#3a5f7d' if not is_dark else '#6da7d8',
        'secondary': '#3498db',
        'accent1': '#27ae60',
        'accent2': '#e74c3c',
        'accent3': '#f39c12',
        'text': '#2c3e50' if not is_dark else '#f0f0f0',
        'text_secondary': '#7f8c8d' if not is_dark else '#c0c0c0',
        'background': '#ecf0f1' if not is_dark else '#1a1f2c',
        'card': '#ffffff' if not is_dark else '#25304c',
        'header': '#2c3e50' if not is_dark else '#1a2436',
        'border': '#bdc3c7' if not is_dark else '#344564'
    }

# Custom CSS for theme-aware styling
st.markdown(f"""
<style>
    /* Main styling */
    .stApp {{
        background-color: var(--background-color);
    }}
    
    /* Titles and headers */
    h1, h2, h3, h4 {{
        color: var(--primary-color) !important;
        border-bottom: 2px solid var(--secondary-color);
        padding-bottom: 0.3rem;
    }}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: var(--header-color);
        color: white;
    }}
    
    .sidebar .sidebar-content {{
        background-color: var(--header-color);
    }}
    
    /* Button styling */
    .stButton>button {{
        background-color: var(--secondary-color);
        color: white;
        border-radius: 4px;
        border: none;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }}
    
    .stButton>button:hover {{
        background-color: #2980b9;
        color: white;
    }}
    
    /* Card styling */
    .card {{
        background: var(--card-color);
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid var(--secondary-color);
        color: var(--text-color);
        border: 1px solid var(--border);
    }}
    
    /* Status indicators */
    .safe {{
        color: var(--accent1);
        font-weight: bold;
    }}
    
    .unsafe {{
        color: var(--accent2);
        font-weight: bold;
    }}
    
    /* Value display */
    .value-display {{
        font-size: 1.5rem;
        font-weight: bold;
        color: var(--secondary-color);
    }}
    
    /* Section headers */
    .section-header {{
        background-color: var(--header-color);
        color: white;
        padding: 10px;
        border-radius: 4px;
        margin-top: 20px;
    }}
    
    /* Material design elements */
    .material-card {{
        background: var(--card-color);
        border: 1px solid var(--border);
        border-radius: 4px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: var(--text-color);
    }}
    
    /* Progress bars */
    .progress-container {{
        height: 8px;
        background-color: var(--border);
        border-radius: 4px;
        margin: 10px 0;
        overflow: hidden;
    }}
    
    .progress-bar {{
        height: 100%;
        background-color: var(--secondary-color);
    }}
    
    /* Text elements */
    body, p, td, li, .stMarkdown {{
        color: var(--text-color) !important;
    }}
    
    /* Table styling */
    table {{
        color: var(--text-color) !important;
    }}
    
    /* Dark mode specific improvements */
    [data-theme="dark"] .material-card,
    [data-theme="dark"] .card {{
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }}
</style>
""", unsafe_allow_html=True)

# Get current colors based on theme
colors = get_colors()

# Add CSS variables for theme colors
st.markdown(f"""
<style>
    :root {{
        --primary-color: {colors['primary']};
        --secondary-color: {colors['secondary']};
        --accent1: {colors['accent1']};
        --accent2: {colors['accent2']};
        --accent3: {colors['accent3']};
        --text-color: {colors['text']};
        --text-secondary: {colors['text_secondary']};
        --background-color: {colors['background']};
        --card-color: {colors['card']};
        --header-color: {colors['header']};
        --border: {colors['border']};
    }}
</style>
""", unsafe_allow_html=True)

# App header
st.markdown(f"""
<div style="background-color:{colors['header']}; padding:20px; border-radius:5px; margin-bottom:20px;">
    <h1 style="color:white; margin:0;">⚙️ FATIH - Industrial Fatigue Assessment Tool</h1>
    <p style="color:#bdc3c7;">Pipeline Integrity Management System for Energy Sector</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="background-color:{colors['header']}; padding:10px; border-radius:4px; margin-bottom:15px;">
        <h3 style="color:white; margin:0;">Pipeline Parameters</h3>
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
    <div style="background-color:{colors['header']}; padding:10px; border-radius:4px; margin-top:15px;">
        <h4 style="color:white; margin:0;">Safety Indicators</h4>
        <p style="color:#bdc3c7; margin:0;">✅ Safe: Value ≤ 1<br>❌ Unsafe: Value > 1</p>
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
        <h4 style="border-bottom: 2px solid {colors['secondary']}; padding-bottom: 5px;">Assessment Protocol</h4>
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
        <p style="text-align: right; color: var(--text-secondary); margin:0;">Status: {'Analysis Complete' if st.session_state.get('run_analysis', False) else 'Ready for Input'}</p>
    </div>
    """, unsafe_allow_html=True)

# Calculations (same as before)

# Main analysis section (same as before)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="background-color:{colors['header']}; padding:20px; border-radius:5px; margin-top:20px;">
    <div style="display: flex; justify-content: space-between; align-items: center; color:white;">
        <div>
            <h4 style="margin:0; color:white;">FATIH v2.0 | Industrial Pipeline Integrity System</h4>
            <p style="margin:0; color:#bdc3c7;">© 2023 Engineering Solutions Ltd.</p>
        </div>
        <div style="text-align: right;">
            <p style="margin:0; color:#bdc3c7;">Technical Support: support@fatih-eng.com</p>
            <p style="margin:0; color:#bdc3c7;">Phone: +1 (800) 555-ENGI</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
