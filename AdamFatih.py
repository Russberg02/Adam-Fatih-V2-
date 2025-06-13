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
    page_title="FATIH - Fatigue Assessment Tool for Integrity & Health",
    page_icon="🔧"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main styling */
    .stApp {
        background-color: #0B2E22;
    }
    
    /* Titles and headers */
    h1, h2, h3 {
        color: white;
        border-bottom: 2px solid #B8E3E9;
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
        padding: 0.5rem 1rem;
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
    
    /* Grid layout */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-bottom: 20px;
    }
    
    /* Value display */
    .value-display {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
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
    if st.button('Run Analysis', use_container_width=True):
        st.session_state.run_analysis = True

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
            <li>Click "Run Analysis" in sidebar</li>
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
if st.session_state.get('run_analysis', False):
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
        st.markdown('<div class="grid-container">', unsafe_allow_html=True)
        
        burst_data = [
            ("Von Mises", pressures['P_vm'], "#3498db"),
            ("Tresca", pressures['P_tresca'], "#2ecc71"),
            ("ASME B31G", pressures['P_asme'], "#9b59b6"),
            ("DNV", pressures['P_dnv'], "#e74c3c"),
            ("PCORRC", pressures['P_pcorrc'], "#f39c12")
        ]
        
        cols = st.columns(5)
        for i, (name, value, color) in enumerate(burst_data):
            with cols[i]:
                st.markdown(f"""
                <div class="card" style="border-left: 5px solid {color};">
                    <h4 style="margin-top: 0;">{name}</h4>
                    <div class="value-display">{value:.2f} MPa</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Stress Analysis
        st.subheader('📈 Stress Analysis')
        stress_col1, stress_col2 = st.columns(2)
        
        with stress_col1:
            st.markdown("""
            <div class="card">
                <h4>Stress Parameters</h4>
                <table style="width:100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 8px;">Max VM Stress</td>
                        <td style="text-align: right; padding: 8px;">{:.2f} MPa</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 8px;">Min VM Stress</td>
                        <td style="text-align: right; padding: 8px;">{:.2f} MPa</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 8px;">Alternating Stress</td>
                        <td style="text-align: right; padding: 8px;">{:.2f} MPa</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 8px;">Mean Stress</td>
                        <td style="text-align: right; padding: 8px;">{:.2f} MPa</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">Endurance Limit</td>
                        <td style="text-align: right; padding: 8px;">{:.2f} MPa</td>
                    </tr>
                </table>
            </div>
            """.format(
                stresses['sigma_vm_max'],
                stresses['sigma_vm_min'],
                stresses['sigma_a'],
                stresses['sigma_m'],
                stresses['Se']
            ), unsafe_allow_html=True)
        
        with stress_col2:
            # Simple stress visualization
            fig, ax = plt.subplots(figsize=(6, 4))
            categories = ['Max Stress', 'Min Stress', 'Amplitude']
            values = [
                stresses['sigma_vm_max'],
                stresses['sigma_vm_min'],
                stresses['sigma_a']
            ]
            colors = ['#3498db', '#2ecc71', '#9b59b6']
            ax.bar(categories, values, color=colors)
            ax.set_title('Stress Distribution', fontsize=12)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            st.pyplot(fig)
        
        # Fatigue Assessment with Safety Status
        st.subheader('🛡️ Fatigue Assessment')
        st.markdown('<div class="grid-container">', unsafe_allow_html=True)
        
        fatigue_data = [
            ("Goodman", fatigue['Goodman'], "σa/Se + σm/UTS = 1", "#3498db"),
            ("Soderberg", fatigue['Soderberg'], "σa/Se + σm/Sy = 1", "#2ecc71"),
            ("Gerber", fatigue['Gerber'], "σa/Se + (σm/UTS)² = 1", "#9b59b6"),
            ("Morrow", fatigue['Morrow'], "σa/Se + σm/(UTS+345) = 1", "#e74c3c"),
            ("ASME-Elliptic", fatigue['ASME-Elliptic'], "(σa/Se)² + (σm/Sy)² = 1", "#f39c12")
        ]
        
        cols = st.columns(5)
        for i, (name, value, equation, color) in enumerate(fatigue_data):
            with cols[i]:
                safe = value <= 1
                status = "✅ Safe" if safe else "❌ Unsafe"
                status_class = "safe" if safe else "unsafe"
                
                st.markdown(f"""
                <div class="card" style="border-left: 5px solid {color};">
                    <h4 style="margin-top: 0;">{name}</h4>
                    <div style="font-size: 0.9em; color: #7f8c8d;">{equation}</div>
                    <div class="value-display">{value:.3f}</div>
                    <div class="{status_class}">{status}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced Plotting with Matplotlib
        st.subheader('📉 Fatigue Analysis Diagram')
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate x-axis values
        x = np.linspace(0, inputs['uts']*1.1, 100)
        
        # Plot all criteria with distinct styles
        ax.plot(x, stresses['Se']*(1 - x/inputs['uts']), 'b-', linewidth=2, label='Goodman')
        ax.plot(x, stresses['Se']*(1 - x/inputs['yield_stress']), 'r-', linewidth=2, label='Soderberg')
        ax.plot(x, stresses['Se']*(1 - (x/inputs['uts'])**2), 'g--', linewidth=2, label='Gerber')
        ax.plot(x, stresses['Se']*(1 - x/stresses['sigma_f']), 'm:', linewidth=2, label='Morrow')
        ax.plot(x, stresses['Se']*np.sqrt(1 - (x/inputs['yield_stress'])**2), 'c-.', linewidth=2, label='ASME-Elliptic')
        
        # Plot operating point
        ax.scatter(stresses['sigma_m'], stresses['sigma_a'], 
                  color='purple', s=120, edgecolor='black', zorder=10,
                  label=f'Operating Point (σm={stresses["sigma_m"]:.1f}, σa={stresses["sigma_a"]:.1f})')
        
        # Mark key points
        ax.scatter(0, stresses['Se'], color='green', s=80, label=f'Se = {stresses["Se"]:.1f} MPa')
        ax.scatter(inputs['uts'], 0, color='blue', s=80, label=f'UTS = {inputs["uts"]:.1f} MPa')
        ax.scatter(inputs['yield_stress'], 0, color='red', s=80, label=f'Sy = {inputs["yield_stress"]:.1f} MPa')
        
        # Formatting
        max_x = max(inputs['uts'], inputs['yield_stress'], stresses['sigma_m']*1.2)
        max_y = max(stresses['Se'], stresses['sigma_a']*1.5)
        ax.set_xlim(0, max_x)
        ax.set_ylim(0, max_y)
        ax.set_xlabel('Mean Stress (σm) [MPa]', fontsize=10)
        ax.set_ylabel('Alternating Stress (σa) [MPa]', fontsize=10)
        ax.set_title('Fatigue Analysis Diagram', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Create custom legend
        ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1), fontsize=9)
        plt.tight_layout()
        
        st.pyplot(fig)

    except ValueError as e:
        st.error(f"🚨 Calculation error: {str(e)}")
    except Exception as e:
        st.error(f"🚨 An unexpected error occurred: {str(e)}")
else:
    st.info("💡 Enter parameters in the sidebar and click 'Run Analysis' to start")

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
