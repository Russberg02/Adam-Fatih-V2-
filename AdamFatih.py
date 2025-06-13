import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.lines import Line2D
import plotly.graph_objects as go

# Configuration
st.set_page_config(
    layout="wide",
    page_title="FATIH - Fatigue Assessment Tool for Integrity & Health",
    page_icon="🔧"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main styling */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Titles and headers */
    h1, h2, h3 {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.3rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #2c3e50;
        color: white;
    }
    
    .sidebar .sidebar-content {
        background-color: #2c3e50;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 4px;
        border: none;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: #2980b9;
        color: white;
    }
    
    /* Dataframe styling */
    .dataframe {
        border: 1px solid #3498db;
        border-radius: 5px;
    }
    
    /* Card styling */
    .card {
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 20px;
    }
    
    /* Status indicators */
    .safe {
        color: #27ae60;
        font-weight: bold;
    }
    
    .unsafe {
        color: #e74c3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# App header with industrial theme
st.title("🔧 FATIH - Fatigue Assessment Tool for Integrity & Health")
st.markdown("### Industrial Pipeline Integrity Management System")

# Sidebar with industrial color scheme
with st.sidebar:
    st.header('⚙️ Pipeline Parameters', divider='blue')
    st.subheader('Dimensional Parameters')
    
    inputs = {
        'pipe_thickness': st.number_input('Pipe Thickness, t (mm)', min_value=0.1, value=10.0),
        'pipe_diameter': st.number_input('Pipe Diameter, D (mm)', min_value=0.1, value=200.0),
        'pipe_length': st.number_input('Pipe Length, L (mm)', min_value=0.1, value=1000.0),
        'corrosion_length': st.number_input('Corrosion Length, Lc (mm)', min_value=0.0, value=50.0),
        'corrosion_depth': st.number_input('Corrosion Depth, Dc (mm)', min_value=0.0, max_value=10.0, value=2.0)
    }
    
    st.subheader('Material Properties')
    inputs['yield_stress'] = st.number_input('Yield Stress, Sy (MPa)', min_value=0.1, value=300.0)
    inputs['uts'] = st.number_input('Ultimate Tensile Strength, UTS (MPa)', min_value=0.1, value=400.0)
    
    st.subheader('Operating Conditions')
    inputs['max_pressure'] = st.slider('Max Operating Pressure (MPa)', 0, 50, 10)
    inputs['min_pressure'] = st.slider('Min Operating Pressure (MPa)', 0, 50, 5)
    
    st.markdown("---")
    st.markdown("**Safety Factors**")
    st.info("""
    - Safe: ✅ (Value ≤ 1)
    - Unsafe: ❌ (Value > 1)
    """)

# Image display
st.subheader('Pipeline Configuration')
col1, col2 = st.columns([1, 2])
with col1:
    st.image("https://www.researchgate.net/profile/Changqing-Gong/publication/313456917/figure/fig1/AS:573308992266241@1513698923813/Schematic-illustration-of-the-geometry-of-a-typical-corrosion-defect.png", 
             caption="Fig. 1: Corrosion defect geometry")
with col2:
    st.markdown("""
    <div class="card">
        <h4>Assessment Guidelines</h4>
        <ul>
            <li>Enter pipeline dimensions and material properties</li>
            <li>Specify operating pressure range</li>
            <li>Review burst pressure calculations</li>
            <li>Analyze stress and fatigue results</li>
            <li>Check safety status for all criteria</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Calculations
def calculate_pressures(inputs):
    t = inputs['pipe_thickness']
    D = inputs['pipe_diameter']
    Lc = inputs['corrosion_length']
    Dc = inputs['corrosion_depth']
    UTS = inputs['uts']
    Sy = inputs['yield_stress']
    
    # Validate inputs to prevent division by zero
    if t <= 0 or D <= 0:
        raise ValueError("Pipe thickness and diameter must be positive values")
    
    # Intact pipe burst pressures
    P_vm = (4 * t * UTS) / (math.sqrt(3) * D)
    P_tresca = (2 * t * UTS) / D
    
    # Corroded pipe burst pressures
    M = math.sqrt(1 + 0.8 * (Lc**2 / (D * t)))  # Folias factor
    
    if Lc <= math.sqrt(20 * D * t):
        P_asme = (2 * t * UTS / D) * ((1 - (2/3) * (Dc/t)) / (1 - (2/3) * (Dc/t) / M))
    else:
        P_asme = (2 * t * UTS / D) * (1 - (Dc/t))
    
    Q = math.sqrt(1 + 0.31 * (Lc**2) / (D * t))
    P_dnv = (2 * UTS * t / (D - t)) * ((1 - (Dc/t)) / (1 - (Dc/(t * Q))))
    P_pcorrc = (2 * t * UTS / D) * (1 - Dc/t)
    
    return {
        'P_vm': P_vm,
        'P_tresca': P_tresca,
        'P_asme': P_asme,
        'P_dnv': P_dnv,
        'P_pcorrc': P_pcorrc
    }

def calculate_stresses(inputs):
    t = inputs['pipe_thickness']
    D = inputs['pipe_diameter']
    Pop_max = inputs['max_pressure']
    Pop_min = inputs['min_pressure']
    UTS = inputs['uts']
    Sy = inputs['yield_stress']
    
    # Principal stresses
    P1_max = Pop_max * D / (2 * t)
    P2_max = Pop_max * D / (4 * t)
    P3_max = 0
    
    P1_min = Pop_min * D / (2 * t)
    P2_min = Pop_min * D / (4 * t)
    P3_min = 0
    
    # Von Mises stresses
    def vm_stress(p1, p2, p3):
        return (1/math.sqrt(2)) * math.sqrt((p1-p2)**2 + (p2-p3)**2 + (p3-p1)**2)
    
    sigma_vm_max = vm_stress(P1_max, P2_max, P3_max)
    sigma_vm_min = vm_stress(P1_min, P2_min, P3_min)
    
    # Fatigue parameters
    sigma_a = (sigma_vm_max - sigma_vm_min) / 2
    sigma_m = (sigma_vm_max + sigma_vm_min) / 2
    Se = 0.5 * UTS
    sigma_f = UTS + 345  # Morrow's fatigue strength coefficient
    
    return {
        'sigma_vm_max': sigma_vm_max,
        'sigma_vm_min': sigma_vm_min,
        'sigma_a': sigma_a,
        'sigma_m': sigma_m,
        'Se': Se,
        'sigma_f': sigma_f
    }

def calculate_fatigue_criteria(sigma_a, sigma_m, Se, UTS, Sy, sigma_f):
    return {
        'Goodman': (sigma_a / Se) + (sigma_m / UTS),
        'Soderberg': (sigma_a / Se) + (sigma_m / Sy),
        'Gerber': (sigma_a / Se) + (sigma_m / UTS)**2,
        'Morrow': (sigma_a / Se) + (sigma_m / sigma_f),
        'ASME-Elliptic': np.sqrt((sigma_a / Se)**2 + (sigma_m / Sy)**2)
    }

# Main analysis section
try:
    # Calculate all parameters
    pressures = calculate_pressures(inputs)
    stresses = calculate_stresses(inputs)
    fatigue = calculate_fatigue_criteria(
        stresses['sigma_a'], stresses['sigma_m'],
        stresses['Se'], inputs['uts'], inputs['yield_stress'],
        stresses['sigma_f']
    )
    
    # Burst Pressure Results in Card Layout
    st.subheader('📊 Burst Pressure Assessment')
    burst_col1, burst_col2, burst_col3, burst_col4, burst_col5 = st.columns(5)
    
    burst_data = [
        ("Von Mises", pressures['P_vm'], "#3498db"),
        ("Tresca", pressures['P_tresca'], "#2ecc71"),
        ("ASME B31G", pressures['P_asme'], "#9b59b6"),
        ("DNV", pressures['P_dnv'], "#e74c3c"),
        ("PCORRC", pressures['P_pcorrc'], "#f39c12")
    ]
    
    for i, (name, value, color) in enumerate(burst_data):
        with [burst_col1, burst_col2, burst_col3, burst_col4, burst_col5][i]:
            st.markdown(f"""
            <div class="card" style="border-left: 5px solid {color};">
                <h4 style="margin-top: 0;">{name}</h4>
                <h3>{value:.2f} MPa</h3>
            </div>
            """, unsafe_allow_html=True)
    
    # Stress Analysis in Tabs
    st.subheader('📈 Stress Analysis')
    tab1, tab2 = st.tabs(["Stress Values", "Visualization"])
    
    with tab1:
        stress_df = pd.DataFrame({
            'Parameter': ['Max VM Stress', 'Min VM Stress', 'Alternating Stress', 
                          'Mean Stress', 'Endurance Limit'],
            'Value (MPa)': [
                stresses['sigma_vm_max'],
                stresses['sigma_vm_min'],
                stresses['sigma_a'],
                stresses['sigma_m'],
                stresses['Se']
            ]
        })
        st.dataframe(stress_df.style.format({"Value (MPa)": "{:.2f}"}), height=210)
    
    with tab2:
        fig_stress = go.Figure()
        fig_stress.add_trace(go.Indicator(
            mode="number",
            value=stresses['sigma_vm_max'],
            title={"text": "Max VM Stress (MPa)"},
            domain={'row': 0, 'column': 0}
        ))
        fig_stress.add_trace(go.Indicator(
            mode="number",
            value=stresses['sigma_vm_min'],
            title={"text": "Min VM Stress (MPa)"},
            domain={'row': 0, 'column': 1}
        ))
        fig_stress.add_trace(go.Indicator(
            mode="number",
            value=stresses['sigma_a'],
            title={"text": "Alternating Stress (MPa)"},
            domain={'row': 1, 'column': 0}
        ))
        fig_stress.add_trace(go.Indicator(
            mode="number",
            value=stresses['sigma_m'],
            title={"text": "Mean Stress (MPa)"},
            domain={'row': 1, 'column': 1}
        ))
        fig_stress.update_layout(
            grid={'rows': 2, 'columns': 2, 'pattern': "independent"},
            template='plotly_white'
        )
        st.plotly_chart(fig_stress, use_container_width=True)
    
    # Fatigue Assessment with Safety Status
    st.subheader('🛡️ Fatigue Assessment')
    
    # Create cards for each criterion
    col1, col2, col3, col4, col5 = st.columns(5)
    
    fatigue_data = [
        ("Goodman", fatigue['Goodman'], "σa/Se + σm/UTS = 1", "#3498db", col1),
        ("Soderberg", fatigue['Soderberg'], "σa/Se + σm/Sy = 1", "#2ecc71", col2),
        ("Gerber", fatigue['Gerber'], "σa/Se + (σm/UTS)² = 1", "#9b59b6", col3),
        ("Morrow", fatigue['Morrow'], "σa/Se + σm/(UTS+345) = 1", "#e74c3c", col4),
        ("ASME-Elliptic", fatigue['ASME-Elliptic'], "(σa/Se)² + (σm/Sy)² = 1", "#f39c12", col5)
    ]
    
    for name, value, equation, color, col in fatigue_data:
        with col:
            safe = value <= 1
            status = "✅ Safe" if safe else "❌ Unsafe"
            status_class = "safe" if safe else "unsafe"
            
            st.markdown(f"""
            <div class="card" style="border-left: 5px solid {color};">
                <h4 style="margin-top: 0;">{name}</h4>
                <div style="font-size: 0.9em; color: #7f8c8d;">{equation}</div>
                <h3>{value:.3f}</h3>
                <div class="{status_class}">{status}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced Plotting with Plotly
    st.subheader('📉 Fatigue Analysis Diagram')
    
    # Generate x-axis values
    x = np.linspace(0, inputs['uts']*1.1, 100)
    
    # Create Plotly figure
    fig = go.Figure()
    
    # Add criteria lines
    fig.add_trace(go.Scatter(
        x=x, y=stresses['Se']*(1 - x/inputs['uts']),
        mode='lines',
        name='Goodman',
        line=dict(color='#3498db', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=x, y=stresses['Se']*(1 - x/inputs['yield_stress']),
        mode='lines',
        name='Soderberg',
        line=dict(color='#2ecc71', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=x, y=stresses['Se']*(1 - (x/inputs['uts'])**2),
        mode='lines',
        name='Gerber',
        line=dict(color='#9b59b6', width=3, dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=x, y=stresses['Se']*(1 - x/stresses['sigma_f']),
        mode='lines',
        name='Morrow',
        line=dict(color='#e74c3c', width=3, dash='dot')
    ))
    fig.add_trace(go.Scatter(
        x=x, y=stresses['Se']*np.sqrt(1 - (x/inputs['yield_stress'])**2),
        mode='lines',
        name='ASME-Elliptic',
        line=dict(color='#f39c12', width=3, dash='dashdot')
    ))
    
    # Add operating point
    fig.add_trace(go.Scatter(
        x=[stresses['sigma_m']],
        y=[stresses['sigma_a']],
        mode='markers',
        name=f'Operating Point (σm={stresses["sigma_m"]:.1f}, σa={stresses["sigma_a"]:.1f})',
        marker=dict(color='#2c3e50', size=12, line=dict(color='white', width=2))
    ))
    
    # Add material points
    fig.add_trace(go.Scatter(
        x=[0],
        y=[stresses['Se']],
        mode='markers',
        name=f'Se = {stresses["Se"]:.1f} MPa',
        marker=dict(color='#27ae60', size=10)
    ))
    fig.add_trace(go.Scatter(
        x=[inputs['uts']],
        y=[0],
        mode='markers',
        name=f'UTS = {inputs["uts"]:.1f} MPa',
        marker=dict(color='#2980b9', size=10)
    ))
    fig.add_trace(go.Scatter(
        x=[inputs['yield_stress']],
        y=[0],
        mode='markers',
        name=f'Sy = {inputs["yield_stress"]:.1f} MPa',
        marker=dict(color='#c0392b', size=10)
    ))
    
    # Formatting
    max_x = max(inputs['uts'], inputs['yield_stress'], stresses['sigma_m']*1.2)
    max_y = max(stresses['Se'], stresses['sigma_a']*1.5)
    
    fig.update_layout(
        title='Fatigue Analysis Diagram with All Criteria',
        xaxis_title='Mean Stress (σm) [MPa]',
        yaxis_title='Alternating Stress (σa) [MPa]',
        xaxis=dict(range=[0, max_x]),
        yaxis=dict(range=[0, max_y]),
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=600,
        margin=dict(l=50, r=50, b=80, t=80, pad=4),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)

except ValueError as e:
    st.error(f"🚨 Calculation error: {str(e)}")
except Exception as e:
    st.error(f"🚨 An unexpected error occurred: {str(e)}")

# References and links in expanders
st.subheader('📚 References & Resources')

with st.expander("Research References"):
    st.markdown("""
    - Xian-Kui Zhu, A comparative study of burst failure models for assessing remaining strength of corroded pipelines, 
      Journal of Pipeline Science and Engineering 1 (2021) 36-50, 
      [DOI:10.1016/j.jpse.2021.01.008](https://doi.org/10.1016/j.jpse.2021.01.008)
    - ASME B31G-2012: Manual for Determining the Remaining Strength of Corroded Pipelines
    - DNV-RP-F101: Corroded Pipelines
    """)

with st.expander("Additional Resources"):
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.markdown("""
        - [Case Study](https://drive.google.com/file/d/1Ako5uVRPYL5k5JeEQ_Xhl9f3pMRBjCJv/view?usp=sharing)
        - [Corroded Pipe Burst Data](https://docs.google.com/spreadsheets/d/1YJ7ziuc_IhU7-MMZOnRmh4h21_gf6h5Z/edit?gid=56754844#gid=56754844)
        """)
    with col_res2:
        st.markdown("""
        - [Pre-Test](https://forms.gle/wPvcgnZAC57MkCxN8)
        - [Post-Test](https://forms.gle/FdiKqpMLzw9ENscA9)
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #7f8c8d;">
    <p>FATIH v2.0 | Pipeline Integrity Management System | © 2023 Engineering Solutions</p>
    <p>For technical support, contact: support@fatih-eng.com</p>
</div>
""", unsafe_allow_html=True)
