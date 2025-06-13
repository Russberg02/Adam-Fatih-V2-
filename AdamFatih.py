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

# High-contrast black and white color palette
BLACK = "#000000"
DARK_GRAY = "#333333"
MEDIUM_GRAY = "#666666"
LIGHT_GRAY = "#e0e0e0"
WHITE = "#FFFFFF"
ACCENT = "#212121"

# Original industrial colors for section headers
SECTION_BLUE = "#2c3e50"      # Deep steel blue
SECTION_GREEN = "#27ae60"     # Safety green
SECTION_RED = "#e74c3c"       # Safety red
SECTION_ORANGE = "#f39c12"    # Safety orange

# Custom CSS for high-contrast styling
st.markdown(f"""
<style>
    /* Main styling with black text */
    .stApp, body, p, td, li, .stMarkdown, h1, h2, h3, h4, h5, h6 {{
        color: #000000 !important;
    }}
    
    .stApp {{
        background-color: {WHITE};
    }}
    
    /* Titles and headers */
    h1, h2, h3 {{
        border-bottom: 2px solid {BLACK};
        padding-bottom: 0.3rem;
    }}
    
    /* Sidebar styling - keep white text for dark background */
    [data-testid="stSidebar"] {{
        background-color: {DARK_GRAY};
        color: white;
    }}
    
    .sidebar .sidebar-content {{
        background-color: {DARK_GRAY};
        color: white;
    }}
    
    /* Button styling */
    .stButton>button {{
        background-color: {BLACK};
        color: white;
        border-radius: 4px;
        border: none;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }}
    
    .stButton>button:hover {{
        background-color: {MEDIUM_GRAY};
        color: white;
    }}
    
    /* Card styling */
    .card {{
        background: white;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid {MEDIUM_GRAY};
        color: #000000;
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
        font-size: 1.5rem;
        font-weight: bold;
        color: #000000;
    }}
    
    /* Material design elements */
    .material-card {{
        background: white;
        border: 1px solid {LIGHT_GRAY};
        border-radius: 4px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: #000000;
    }}
    
    /* Industrial progress bars */
    .progress-container {{
        height: 8px;
        background-color: {LIGHT_GRAY};
        border-radius: 4px;
        margin: 10px 0;
        overflow: hidden;
    }}
    
    .progress-bar {{
        height: 100%;
        background-color: {BLACK};
    }}
</style>
""", unsafe_allow_html=True)

# App header with high contrast theme
st.markdown(f"""
<div style="background-color:{BLACK}; padding:20px; border-radius:5px; margin-bottom:20px;">
    <h1 style="color:white; margin:0;">⚙️ FATIH - Industrial Fatigue Assessment Tool</h1>
    <p style="color:#b0b0b0;">Pipeline Integrity Management System for Energy Sector</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with high contrast scheme
with st.sidebar:
    st.markdown(f"""
    <div style="background-color:{BLACK}; padding:10px; border-radius:4px; margin-bottom:15px;">
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
    <div style="background-color:{BLACK}; padding:10px; border-radius:4px; margin-top:15px;">
        <h4 style="color:white; margin:0;">Safety Indicators</h4>
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
        <h4 style="border-bottom: 2px solid {BLACK}; padding-bottom: 5px;">Assessment Protocol</h4>
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
        
        # Burst Pressure Results in Card Layout (with colored section header)
        st.markdown(f"""
        <div style="background-color:{SECTION_BLUE}; padding:10px; border-radius:4px; margin-top:20px;">
            <h3 style="color:white; margin:0;">📊 Burst Pressure Assessment</h3>
        </div>
        """, unsafe_allow_html=True)
        
        burst_cols = st.columns(5)
        burst_data = [
            ("Von Mises", pressures['P_vm'], BLACK),
            ("Tresca", pressures['P_tresca'], DARK_GRAY),
            ("ASME B31G", pressures['P_asme'], MEDIUM_GRAY),
            ("DNV", pressures['P_dnv'], ACCENT),
            ("PCORRC", pressures['P_pcorrc'], BLACK)
        ]
        
        for i, (name, value, color) in enumerate(burst_data):
            with burst_cols[i]:
                st.markdown(f"""
                <div class="card">
                    <h4 style="margin-top: 0;">{name}</h4>
                    <div class="value-display">{value:.2f} MPa</div>
                    <div style="height: 4px; background: {LIGHT_GRAY}; margin: 10px 0;">
                        <div style="height: 4px; background: {color}; width: {min(100, value/10*100)}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Stress Analysis (with colored section header)
        st.markdown(f"""
        <div style="background-color:{SECTION_GREEN}; padding:10px; border-radius:4px; margin-top:20px;">
            <h3 style="color:white; margin:0;">📈 Stress Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        stress_col1, stress_col2 = st.columns([1, 1])
        
        with stress_col1:
            st.markdown(f"""
            <div class="material-card">
                <h4>Stress Parameters</h4>
                <table style="width:100%; border-collapse: collapse; font-size: 0.95rem;">
                    <tr style="border-bottom: 1px solid {LIGHT_GRAY};">
                        <td style="padding: 8px;">Max VM Stress</td>
                        <td style="text-align: right; padding: 8px; font-weight: bold;">{stresses['sigma_vm_max']:.2f} MPa</td>
                    </tr>
                    <tr style="border-bottom: 1px solid {LIGHT_GRAY};">
                        <td style="padding: 8px;">Min VM Stress</td>
                        <td style="text-align: right; padding: 8px; font-weight: bold;">{stresses['sigma_vm_min']:.2f} MPa</td>
                    </tr>
                    <tr style="border-bottom: 1px solid {LIGHT_GRAY};">
                        <td style="padding: 8px;">Alternating Stress</td>
                        <td style="text-align: right; padding: 8px; font-weight: bold;">{stresses['sigma_a']:.2f} MPa</td>
                    </tr>
                    <tr style="border-bottom: 1px solid {LIGHT_GRAY};">
                        <td style="padding: 8px;">Mean Stress</td>
                        <td style="text-align: right; padding: 8px; font-weight: bold;">{stresses['sigma_m']:.2f} MPa</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">Endurance Limit</td>
                        <td style="text-align: right; padding: 8px; font-weight: bold;">{stresses['Se']:.2f} MPa</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        with stress_col2:
            # Simple stress visualization
            fig, ax = plt.subplots(figsize=(6, 4))
            categories = ['Max Stress', 'Min Stress', 'Amplitude']
            values = [
                stresses['sigma_vm_max'],
                stresses['sigma_vm_min'],
                stresses['sigma_a']
            ]
            colors = [BLACK, MEDIUM_GRAY, DARK_GRAY]
            bars = ax.bar(categories, values, color=colors)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f} MPa',
                        ha='center', va='bottom', fontsize=9)
            
            ax.set_ylim(0, max(values) * 1.2)
            ax.set_title('Stress Distribution', fontsize=10)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
        
        # Fatigue Assessment (with colored section header)
        st.markdown(f"""
        <div style="background-color:{SECTION_RED}; padding:10px; border-radius:4px; margin-top:20px;">
            <h3 style="color:white; margin:0;">🛡️ Fatigue Assessment</h3>
        </div>
        """, unsafe_allow_html=True)
        
        fatigue_cols = st.columns(5)
        fatigue_data = [
            ("Goodman", fatigue['Goodman'], "σa/Se + σm/UTS = 1", BLACK),
            ("Soderberg", fatigue['Soderberg'], "σa/Se + σm/Sy = 1", DARK_GRAY),
            ("Gerber", fatigue['Gerber'], "σa/Se + (σm/UTS)² = 1", MEDIUM_GRAY),
            ("Morrow", fatigue['Morrow'], "σa/Se + σm/(UTS+345) = 1", ACCENT),
            ("ASME-Elliptic", fatigue['ASME-Elliptic'], "(σa/Se)² + (σm/Sy)² = 1", BLACK)
        ]
        
        for i, (name, value, equation, color) in enumerate(fatigue_data):
            with fatigue_cols[i]:
                safe = value <= 1
                status = "✅ Safe" if safe else "❌ Unsafe"
                status_class = "safe" if safe else "unsafe"
                
                st.markdown(f"""
                <div class="card">
                    <h4 style="margin-top: 0;">{name}</h4>
                    <div style="font-size: 0.85em; margin-bottom: 10px;">{equation}</div>
                    <div class="value-display">{value:.3f}</div>
                    <div class="{status_class}" style="margin-top: 10px;">{status}</div>
                    <div style="height: 4px; background: {LIGHT_GRAY}; margin: 10px 0;">
                        <div style="height: 4px; background: {color}; width: {min(100, value*100)}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Enhanced Plotting with Matplotlib (with colored section header)
        st.markdown(f"""
        <div style="background-color:{SECTION_ORANGE}; padding:10px; border-radius:4px; margin-top:20px;">
            <h3 style="color:white; margin:0;">📉 Fatigue Analysis Diagram</h3>
        </div>
        """, unsafe_allow_html=True)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate x-axis values
        x = np.linspace(0, inputs['uts']*1.1, 100)
        
        # Plot all criteria with distinct styles in grayscale
        ax.plot(x, stresses['Se']*(1 - x/inputs['uts']), color='black', linewidth=2, label='Goodman')
        ax.plot(x, stresses['Se']*(1 - x/inputs['yield_stress']), color='black', linestyle='--', linewidth=2, label='Soderberg')
        ax.plot(x, stresses['Se']*(1 - (x/inputs['uts'])**2), color='black', linestyle=':', linewidth=2, label='Gerber')
        ax.plot(x, stresses['Se']*(1 - x/stresses['sigma_f']), color='black', linestyle='-.', linewidth=2, label='Morrow')
        ax.plot(x, stresses['Se']*np.sqrt(1 - (x/inputs['yield_stress'])**2), color='gray', linewidth=2, label='ASME-Elliptic')
        
        # Plot operating point
        ax.scatter(stresses['sigma_m'], stresses['sigma_a'], 
                  color='black', s=120, edgecolor='white', zorder=10,
                  label=f'Operating Point (σm={stresses["sigma_m"]:.1f}, σa={stresses["sigma_a"]:.1f})')
        
        # Mark key points
        ax.scatter(0, stresses['Se'], color='black', s=80, label=f'Se = {stresses["Se"]:.1f} MPa')
        ax.scatter(inputs['uts'], 0, color='black', s=80, label=f'UTS = {inputs["uts"]:.1f} MPa')
        ax.scatter(inputs['yield_stress'], 0, color='black', s=80, label=f'Sy = {inputs["yield_stress"]:.1f} MPa')
        
        # Formatting
        max_x = max(inputs['uts'], inputs['yield_stress'], stresses['sigma_m']*1.2)
        max_y = max(stresses['Se'], stresses['sigma_a']*1.5)
        ax.set_xlim(0, max_x)
        ax.set_ylim(0, max_y)
        ax.set_xlabel('Mean Stress (σm) [MPa]', fontsize=10)
        ax.set_ylabel('Alternating Stress (σa) [MPa]', fontsize=10)
        ax.set_title('Fatigue Analysis Diagram', fontsize=12, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_facecolor(WHITE)
        
        # Create custom legend
        ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1), fontsize=9)
        plt.tight_layout()
        
        st.pyplot(fig)

    except ValueError as e:
        st.error(f"🚨 Calculation error: {str(e)}")
    except Exception as e:
        st.error(f"🚨 An unexpected error occurred: {str(e)}")
else:
    st.markdown(f"""
    <div class="material-card">
        <h4 style="text-align: center;">⏳ Ready for Analysis</h4>
        <p style="text-align: center;">
            Enter parameters in the sidebar and click 'Run Analysis' to start
        </p>
        <div class="progress-container">
            <div class="progress-bar" style="width: 30%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# References and links in expanders
st.markdown(f"""
<div style="background-color:{MEDIUM_GRAY}; padding:10px; border-radius:4px; margin-top:20px;">
    <h3 style="color:white; margin:0;">📚 References & Resources</h3>
</div>
""", unsafe_allow_html=True)

ref_col1, ref_col2 = st.columns([1, 1])
with ref_col1:
    with st.expander("Research References", expanded=True):
        st.markdown("""
        - **Xian-Kui Zhu** (2021)  
          *Journal of Pipeline Science and Engineering*  
          Comparative study of burst failure models for corroded pipelines  
          [DOI:10.1016/j.jpse.2021.01.008](https://doi.org/10.1016/j.jpse.2021.01.008)
        
        - **ASME B31G-2012**  
          Manual for Determining the Remaining Strength of Corroded Pipelines
        
        - **DNV-RP-F101**  
          Corroded Pipelines Standard
        """)

with ref_col2:
    with st.expander("Additional Resources", expanded=True):
        st.markdown("""
        - [Case Study: Pipeline Failure Analysis](https://drive.google.com/file/d/1Ako5uVRPYL5k5JeEQ_Xhl9f3pMRBjCJv/view?usp=sharing)
        - [Corroded Pipe Burst Database](https://docs.google.com/spreadsheets/d/1YJ7ziuc_IhU7-MMZOnRmh4h21_gf6h5Z/edit?gid=56754844#gid=56754844)
        - [Pre-Assessment Questionnaire](https://forms.gle/wPvcgnZAC57MkCxN8)
        - [Post-Assessment Feedback](https://forms.gle/FdiKqpMLzw9ENscA9)
        """)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="background-color:{BLACK}; padding:20px; border-radius:5px; margin-top:20px;">
    <div style="display: flex; justify-content: space-between; align-items: center; color:white;">
        <div>
            <h4 style="margin:0; color:white;">FATIH v2.0 | Industrial Pipeline Integrity System</h4>
            <p style="margin:0; color:#b0b0b0;">© 2023 Engineering Solutions Ltd.</p>
        </div>
        <div style="text-align: right;">
            <p style="margin:0; color:#b0b0b0;">Technical Support: support@fatih-eng.com</p>
            <p style="margin:0; color:#b0b0b0;">Phone: +1 (800) 555-ENGI</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
