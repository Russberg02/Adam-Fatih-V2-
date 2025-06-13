import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

# Configuration
st.set_page_config(
    layout="wide",
    page_title="FATIH - Industrial Fatigue Assessment",
    page_icon="⚙️"
)

# Industrial color palette
INDUSTRIAL_BLUE = "#2c3e50"
SAFETY_BLUE = "#3498db"
SAFETY_GREEN = "#27ae60"
SAFETY_RED = "#e74c3c"
SAFETY_ORANGE = "#f39c12"
ACCENT_PURPLE = "#9b59b6"
LIGHT_GRAY = "#ecf0f1"

# Custom CSS for clean industrial styling
st.markdown(f"""
<style>
    body, p, td, li, .stMarkdown, h1, h2, h3, h4, h5, h6 {{
        color: #000000 !important;
    }}
    
    .stApp {{
        background-color: {LIGHT_GRAY};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    h1, h2, h3, h4 {{
        border-bottom: 2px solid {SAFETY_BLUE};
        padding-bottom: 0.3rem;
        margin-top: 0.5rem;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {INDUSTRIAL_BLUE};
    }}
    
    .stButton>button {{
        background-color: {SAFETY_BLUE};
        color: white;
        border-radius: 4px;
        border: none;
        font-weight: bold;
        padding: 0.5rem 1rem;
        width: 100%;
    }}
    
    .card {{
        background: white;
        border-radius: 5px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 20px;
        border-left: 4px solid {SAFETY_BLUE};
    }}
    
    .value-display {{
        font-size: 1.8rem;
        font-weight: bold;
        color: {INDUSTRIAL_BLUE};
        text-align: center;
        margin: 10px 0;
    }}
    
    .section-header {{
        background-color: {INDUSTRIAL_BLUE};
        color: white;
        padding: 12px 15px;
        border-radius: 4px;
        margin: 25px 0 15px 0;
    }}
    
    .material-card {{
        background: white;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }}
    
    .progress-container {{
        height: 8px;
        background-color: #e0e0e0;
        border-radius: 4px;
        margin: 15px 0;
    }}
    
    .progress-bar {{
        height: 100%;
        background-color: {SAFETY_BLUE};
    }}
    
    .status-safe {{
        color: {SAFETY_GREEN};
        font-weight: bold;
        font-size: 1.1rem;
    }}
    
    .status-unsafe {{
        color: {SAFETY_RED};
        font-weight: bold;
        font-size: 1.1rem;
    }}
    
    .reference-box {{
        background-color: #f8f9fa;
        border-left: 3px solid {SAFETY_BLUE};
        padding: 12px 15px;
        margin: 10px 0;
        border-radius: 0 4px 4px 0;
    }}
    
    .footer {{
        background-color: {INDUSTRIAL_BLUE};
        color: white;
        padding: 20px;
        border-radius: 5px;
        margin-top: 30px;
    }}
</style>
""", unsafe_allow_html=True)

# App header
st.markdown(f"""
<div style="background-color:{INDUSTRIAL_BLUE}; padding:25px; border-radius:5px; margin-bottom:25px;">
    <h1 style="color:white; margin:0; text-align:center;">⚙️ FATIH - Industrial Fatigue Assessment Tool</h1>
    <p style="color:#bdc3c7; text-align:center; margin:5px 0 0 0;">Pipeline Integrity Management System</p>
</div>
""", unsafe_allow_html=True)

# ======================
# SIDEBAR CONFIGURATION
# ======================
with st.sidebar:
    st.markdown(f"""
    <div style="background-color:{INDUSTRIAL_BLUE}; padding:12px; border-radius:4px; margin-bottom:20px;">
        <h3 style="color:white; margin:0; text-align:center;">Pipeline Parameters</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Dimensional Parameters
    with st.expander("📏 Dimensional Parameters", expanded=True):
        pipe_thickness = st.number_input('Pipe Thickness, t (mm)', min_value=0.1, value=10.0)
        pipe_diameter = st.number_input('Pipe Diameter, D (mm)', min_value=0.1, value=200.0)
        pipe_length = st.number_input('Pipe Length, L (mm)', min_value=0.1, value=1000.0)
        corrosion_length = st.number_input('Corrosion Length, Lc (mm)', min_value=0.0, value=50.0)
        corrosion_depth = st.number_input('Corrosion Depth, Dc (mm)', min_value=0.0, max_value=10.0, value=2.0)
    
    # Material Properties
    with st.expander("🧱 Material Properties", expanded=True):
        yield_stress = st.number_input('Yield Stress, Sy (MPa)', min_value=0.1, value=300.0)
        uts = st.number_input('Ultimate Tensile Strength, UTS (MPa)', min_value=0.1, value=400.0)
    
    # Operating Conditions
    with st.expander("📊 Operating Conditions", expanded=True):
        max_pressure = st.slider('Max Operating Pressure (MPa)', 0, 50, 10)
        min_pressure = st.slider('Min Operating Pressure (MPa)', 0, 50, 5)
    
    st.markdown("---")
    st.markdown(f"""
    <div style="background-color:{INDUSTRIAL_BLUE}; padding:12px; border-radius:4px; margin-top:15px;">
        <h4 style="color:white; margin:0;">Safety Indicators</h4>
        <p style="color:#bdc3c7; margin:3px 0 0 0;">✅ Safe: Value ≤ 1<br>❌ Unsafe: Value > 1</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Run Analysis', use_container_width=True, type="primary"):
            st.session_state.run_analysis = True
    with col2:
        if st.button('Reset Values', use_container_width=True):
            st.session_state.run_analysis = False

# ======================
# MAIN CONTENT
# ======================

# Pipeline Configuration Section
st.subheader('Pipeline Configuration')
col1, col2 = st.columns([1, 2])
with col1:
    st.image("https://www.researchgate.net/profile/Changqing-Gong/publication/313456917/figure/fig1/AS:573308992266241@1513698923813/Schematic-illustration-of-the-geometry-of-a-typical-corrosion-defect.png", 
             caption="Fig. 1: Corrosion defect geometry")
with col2:
    st.markdown(f"""
    <div class="material-card">
        <h4>Assessment Protocol</h4>
        <ol>
            <li>Enter pipeline dimensions and material properties</li>
            <li>Specify operating pressure range</li>
            <li>Click "Run Analysis" to perform assessment</li>
            <li>Review burst pressure calculations</li>
            <li>Analyze stress and fatigue results</li>
            <li>Check safety status for all criteria</li>
        </ol>
        <div class="progress-container">
            <div class="progress-bar" style="width: {'70%' if st.session_state.get('run_analysis', False) else '15%'};"></div>
        </div>
        <p style="text-align: right; font-weight:bold; margin:5px 0 0 0;">
            Status: {'Analysis Complete' if st.session_state.get('run_analysis', False) else 'Ready for Input'}
        </p>
    </div>
    """, unsafe_allow_html=True)

# ======================
# CALCULATION FUNCTIONS
# ======================
def calculate_pressures(t, D, Lc, Dc, UTS):
    """Calculate various burst pressures using different models"""
    # Intact pipe burst pressures
    P_vm = (4 * t * UTS) / (math.sqrt(3) * D)
    P_tresca = (2 * t * UTS) / D
    
    # Corroded pipe burst pressures
    M = math.sqrt(1 + 0.8 * (Lc**2 / (D * t)))
    
    if Lc <= math.sqrt(20 * D * t):
        P_asme = (2 * t * UTS / D) * ((1 - (2/3) * (Dc/t)) / (1 - (2/3) * (Dc/t) / M))
    else:
        P_asme = (2 * t * UTS / D) * (1 - (Dc/t))
    
    Q = math.sqrt(1 + 0.31 * (Lc**2) / (D * t))
    P_dnv = (2 * UTS * t / (D - t)) * ((1 - (Dc/t)) / (1 - (Dc/(t * Q))))
    P_pcorrc = (2 * t * UTS / D) * (1 - Dc/t)
    
    return P_vm, P_tresca, P_asme, P_dnv, P_pcorrc

def calculate_stresses(t, D, max_pressure, min_pressure):
    """Calculate stress parameters"""
    # Principal stresses
    P1_max = max_pressure * D / (2 * t)
    P2_max = max_pressure * D / (4 * t)
    P3_max = 0
    
    P1_min = min_pressure * D / (2 * t)
    P2_min = min_pressure * D / (4 * t)
    P3_min = 0
    
    # Von Mises stresses calculation
    def vm_stress(p1, p2, p3):
        return (1/math.sqrt(2)) * math.sqrt((p1-p2)**2 + (p2-p3)**2 + (p3-p1)**2)
    
    sigma_vm_max = vm_stress(P1_max, P2_max, P3_max)
    sigma_vm_min = vm_stress(P1_min, P2_min, P3_min)
    
    # Fatigue parameters
    sigma_a = (sigma_vm_max - sigma_vm_min) / 2
    sigma_m = (sigma_vm_max + sigma_vm_min) / 2
    Se = 0.5 * uts
    sigma_f = uts + 345  # Morrow's fatigue strength coefficient
    
    return sigma_vm_max, sigma_vm_min, sigma_a, sigma_m, Se, sigma_f

def calculate_fatigue_criteria(sigma_a, sigma_m, Se, UTS, Sy, sigma_f):
    """Calculate fatigue criteria"""
    return {
        'Goodman': (sigma_a / Se) + (sigma_m / UTS),
        'Soderberg': (sigma_a / Se) + (sigma_m / Sy),
        'Gerber': (sigma_a / Se) + (sigma_m / UTS)**2,
        'Morrow': (sigma_a / Se) + (sigma_m / sigma_f),
        'ASME-Elliptic': np.sqrt((sigma_a / Se)**2 + (sigma_m / Sy)**2)
    }

# ======================
# ANALYSIS SECTION
# ======================
if st.session_state.get('run_analysis', False):
    try:
        # Burst Pressure Calculation
        st.markdown("""
        <div class="section-header">
            <h3 style="color:white; margin:0;">📊 Burst Pressure Assessment</h3>
        </div>
        """, unsafe_allow_html=True)
        
        P_vm, P_tresca, P_asme, P_dnv, P_pcorrc = calculate_pressures(
            pipe_thickness, pipe_diameter, corrosion_length, corrosion_depth, uts
        )
        
        # Display burst pressure results
        burst_cols = st.columns(5)
        burst_data = [
            ("Von Mises", P_vm, SAFETY_BLUE),
            ("Tresca", P_tresca, SAFETY_GREEN),
            ("ASME B31G", P_asme, ACCENT_PURPLE),
            ("DNV", P_dnv, SAFETY_RED),
            ("PCORRC", P_pcorrc, SAFETY_ORANGE)
        ]
        
        for i, (name, value, color) in enumerate(burst_data):
            with burst_cols[i]:
                st.markdown(f"""
                <div class="card" style="border-left: 4px solid {color};">
                    <h4 style="margin-top: 0; text-align:center;">{name}</h4>
                    <div class="value-display">{value:.2f} MPa</div>
                    <div style="height: 4px; background: #e0e0e0; margin: 10px 0;">
                        <div style="height: 4px; background: {color}; width: {min(100, value/10*100)}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Stress Analysis
        st.markdown("""
        <div class="section-header">
            <h3 style="color:white; margin:0;">📈 Stress Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        stress_col1, stress_col2 = st.columns([1, 1])
        
        with stress_col1:
            sigma_vm_max, sigma_vm_min, sigma_a, sigma_m, Se, sigma_f = calculate_stresses(
                pipe_thickness, pipe_diameter, max_pressure, min_pressure
            )
            
            st.markdown(f"""
            <div class="material-card">
                <h4>Stress Parameters</h4>
                <table style="width:100%; border-collapse: collapse; font-size: 1rem;">
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px;">Max VM Stress</td>
                        <td style="text-align: right; padding: 10px; font-weight: bold;">{sigma_vm_max:.2f} MPa</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px;">Min VM Stress</td>
                        <td style="text-align: right; padding: 10px; font-weight: bold;">{sigma_vm_min:.2f} MPa</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px;">Alternating Stress</td>
                        <td style="text-align: right; padding: 10px; font-weight: bold;">{sigma_a:.2f} MPa</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px;">Mean Stress</td>
                        <td style="text-align: right; padding: 10px; font-weight: bold;">{sigma_m:.2f} MPa</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px;">Endurance Limit</td>
                        <td style="text-align: right; padding: 10px; font-weight: bold;">{Se:.2f} MPa</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        with stress_col2:
            # Stress visualization
            fig, ax = plt.subplots(figsize=(6, 4))
            categories = ['Max Stress', 'Min Stress', 'Amplitude']
            values = [sigma_vm_max, sigma_vm_min, sigma_a]
            colors = [SAFETY_BLUE, SAFETY_RED, ACCENT_PURPLE]
            bars = ax.bar(categories, values, color=colors)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f} MPa',
                        ha='center', va='bottom', fontsize=10)
            
            ax.set_ylim(0, max(values) * 1.2)
            ax.set_title('Stress Distribution', fontsize=12)
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
        
        # Fatigue Assessment
        st.markdown("""
        <div class="section-header">
            <h3 style="color:white; margin:0;">🛡️ Fatigue Assessment</h3>
        </div>
        """, unsafe_allow_html=True)
        
        fatigue = calculate_fatigue_criteria(
            sigma_a, sigma_m, Se, uts, yield_stress, sigma_f
        )
        
        # Display fatigue criteria
        fatigue_cols = st.columns(5)
        fatigue_data = [
            ("Goodman", fatigue['Goodman'], "σa/Se + σm/UTS = 1", SAFETY_BLUE),
            ("Soderberg", fatigue['Soderberg'], "σa/Se + σm/Sy = 1", SAFETY_GREEN),
            ("Gerber", fatigue['Gerber'], "σa/Se + (σm/UTS)² = 1", ACCENT_PURPLE),
            ("Morrow", fatigue['Morrow'], "σa/Se + σm/(UTS+345) = 1", SAFETY_RED),
            ("ASME-Elliptic", fatigue['ASME-Elliptic'], "(σa/Se)² + (σm/Sy)² = 1", SAFETY_ORANGE)
        ]
        
        for i, (name, value, equation, color) in enumerate(fatigue_data):
            with fatigue_cols[i]:
                safe = value <= 1
                status = "✅ Safe" if safe else "❌ Unsafe"
                status_class = "status-safe" if safe else "status-unsafe"
                
                st.markdown(f"""
                <div class="card" style="border-left: 4px solid {color};">
                    <h4 style="margin-top: 0; text-align:center;">{name}</h4>
                    <div style="font-size: 0.9em; text-align:center; margin-bottom: 12px;">{equation}</div>
                    <div class="value-display">{value:.3f}</div>
                    <div class="{status_class}" style="text-align:center; margin-top: 15px;">{status}</div>
                    <div style="height: 4px; background: #e0e0e0; margin: 15px 0;">
                        <div style="height: 4px; background: {color}; width: {min(100, value*100)}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Fatigue Analysis Diagram
        st.markdown("""
        <div class="section-header">
            <h3 style="color:white; margin:0;">📉 Fatigue Analysis Diagram</h3>
        </div>
        """, unsafe_allow_html=True)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate x-axis values
        x = np.linspace(0, uts*1.1, 100)
        
        # Plot all criteria
        ax.plot(x, Se*(1 - x/uts), color=SAFETY_BLUE, linewidth=2, label='Goodman')
        ax.plot(x, Se*(1 - x/yield_stress), color=SAFETY_GREEN, linewidth=2, label='Soderberg')
        ax.plot(x, Se*(1 - (x/uts)**2), color=ACCENT_PURPLE, linestyle='--', linewidth=2, label='Gerber')
        ax.plot(x, Se*(1 - x/sigma_f), color=SAFETY_RED, linestyle=':', linewidth=2, label='Morrow')
        ax.plot(x, Se*np.sqrt(1 - (x/yield_stress)**2), color=SAFETY_ORANGE, linestyle='-.', linewidth=2, label='ASME-Elliptic')
        
        # Plot operating point
        ax.scatter(sigma_m, sigma_a, color=INDUSTRIAL_BLUE, s=120, 
                  edgecolor='white', zorder=10,
                  label=f'Operating Point (σm={sigma_m:.1f}, σa={sigma_a:.1f})')
        
        # Mark key points
        ax.scatter(0, Se, color=SAFETY_GREEN, s=80, label=f'Se = {Se:.1f} MPa')
        ax.scatter(uts, 0, color=SAFETY_BLUE, s=80, label=f'UTS = {uts:.1f} MPa')
        ax.scatter(yield_stress, 0, color=SAFETY_RED, s=80, label=f'Sy = {yield_stress:.1f} MPa')
        
        # Formatting
        max_x = max(uts, yield_stress, sigma_m*1.2)
        max_y = max(Se, sigma_a*1.5)
        ax.set_xlim(0, max_x)
        ax.set_ylim(0, max_y)
        ax.set_xlabel('Mean Stress (σm) [MPa]', fontsize=11)
        ax.set_ylabel('Alternating Stress (σa) [MPa]', fontsize=11)
        ax.set_title('Fatigue Analysis Diagram', fontsize=13, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_facecolor('#f8f9fa')
        
        # Create custom legend
        ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1), fontsize=10)
        plt.tight_layout()
        
        st.pyplot(fig)

    except Exception as e:
        st.error(f"🚨 An error occurred during analysis: {str(e)}")
else:
    st.markdown(f"""
    <div class="material-card">
        <h4 style="text-align: center; margin-top:10px;">⏳ Ready for Analysis</h4>
        <p style="text-align: center; margin:15px 0;">
            Enter parameters in the sidebar and click 'Run Analysis' to start
        </p>
        <div class="progress-container">
            <div class="progress-bar" style="width: 30%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ======================
# REFERENCES & FOOTER
# ======================
st.markdown("""
<div class="section-header">
    <h3 style="color:white; margin:0;">📚 References & Resources</h3>
</div>
""", unsafe_allow_html=True)

ref_col1, ref_col2 = st.columns([1, 1])
with ref_col1:
    st.markdown("""
    <div class="reference-box">
        <h5>Research References</h5>
        <p><strong>Xian-Kui Zhu (2021)</strong><br>
        <em>Journal of Pipeline Science and Engineering</em><br>
        Comparative study of burst failure models for corroded pipelines<br>
        DOI:10.1016/j.jpse.2021.01.008</p>
        
        <p><strong>ASME B31G-2012</strong><br>
        Manual for Determining the Remaining Strength of Corroded Pipelines</p>
        
        <p><strong>DNV-RP-F101</strong><br>
        Corroded Pipelines Standard</p>
    </div>
    """, unsafe_allow_html=True)

with ref_col2:
    st.markdown("""
    <div class="reference-box">
        <h5>Additional Resources</h5>
        <p>• <a href="#" style="color:{INDUSTRIAL_BLUE};">Case Study: Pipeline Failure Analysis</a></p>
        <p>• <a href="#" style="color:{INDUSTRIAL_BLUE};">Corroded Pipe Burst Database</a></p>
        <p>• <a href="#" style="color:{INDUSTRIAL_BLUE};">Pre-Assessment Questionnaire</a></p>
        <p>• <a href="#" style="color:{INDUSTRIAL_BLUE};">Post-Assessment Feedback</a></p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h4 style="margin:0;">FATIH v2.0 | Industrial Pipeline Integrity System</h4>
            <p style="margin:5px 0 0 0; color:#bdc3c7;">© 2023 Engineering Solutions Ltd.</p>
        </div>
        <div style="text-align: right;">
            <p style="margin:0;">Technical Support: support@fatih-eng.com</p>
            <p style="margin:5px 0 0 0; color:#bdc3c7;">Phone: +1 (800) 555-ENGI</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
