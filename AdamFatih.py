import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D

# Configuration
st.set_page_config(
    layout="wide",
    page_title="FATIH - Industrial Fatigue Assessment",
    page_icon="⚙️"
)

# High-contrast color palette optimized for analysis
COLORS = {
    'background': '#f0f2f6',
    'card': '#ffffff',
    'text': '#000000',
    'accent': '#1f77b4',
    'secondary': '#ff7f0e',
    'goodman': '#1f77b4',     # Blue
    'soderberg': '#ff7f0e',   # Orange
    'gerber': '#2ca02c',      # Green
    'morrow': '#d62728',      # Red
    'asme': '#9467bd',        # Purple
    'safe': '#2ca02c',        # Green
    'unsafe': '#d62728',      # Red
    'burst': '#17becf',       # Teal
    'stress': '#e377c2',      # Pink
    'fatigue': '#bcbd22'      # Olive
}

# Custom CSS for clean, functional styling
st.markdown(f"""
<style>
    /* Main styling */
    .stApp {{
        background-color: {COLORS['background']};
        color: {COLORS['text']};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* Titles and headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['accent']} !important;
        padding-bottom: 0.3rem;
    }}
    
    /* Card styling */
    .card {{
        background: {COLORS['card']};
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid {COLORS['accent']};
    }}
    
    /* Status indicators */
    .safe {{
        color: {COLORS['safe']};
        font-weight: bold;
    }}
    
    .unsafe {{
        color: {COLORS['unsafe']};
        font-weight: bold;
    }}
    
    /* Value display */
    .value-display {{
        font-size: 1.6rem;
        font-weight: bold;
        color: {COLORS['accent']};
    }}
    
    /* Section headers */
    .section-header {{
        background-color: {COLORS['card']};
        padding: 10px 15px;
        border-radius: 4px;
        margin: 20px 0;
        border-left: 4px solid {COLORS['accent']};
    }}
    
    /* Button styling */
    .stButton>button {{
        background-color: {COLORS['accent']};
        color: white;
        border-radius: 4px;
        border: none;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }}
    
    .stButton>button:hover {{
        background-color: {COLORS['secondary']};
        color: white;
    }}
    
    /* Table styling */
    table {{
        border: 1px solid #ddd !important;
    }}
    
    /* Progress bar */
    .progress-bar {{
        height: 8px;
        background-color: #e0e0e0;
        border-radius: 4px;
        margin: 10px 0;
        overflow: hidden;
    }}
    
    .progress-fill {{
        height: 100%;
        background-color: {COLORS['accent']};
    }}
</style>
""", unsafe_allow_html=True)

# App header
st.markdown(f"""
<div style="background-color:{COLORS['accent']}; padding:20px; border-radius:5px; margin-bottom:20px;">
    <h1 style="color:white; margin:0;">⚙️ FATIH - Industrial Fatigue Assessment Tool</h1>
    <p style="color:#e0e0e0;">Pipeline Integrity Management System for Energy Sector</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for configurations
if 'configurations' not in st.session_state:
    st.session_state.configurations = [{
        'name': "Default Configuration",
        'pipe_thickness': 10.0,
        'pipe_diameter': 200.0,
        'pipe_length': 1000.0,
        'corrosion_length': 50.0,
        'corrosion_depth': 2.0,
        'yield_stress': 300.0,
        'uts': 400.0,
        'max_pressure': 10,
        'min_pressure': 5
    }]
    
if 'active_config' not in st.session_state:
    st.session_state.active_config = 0

# Sidebar for configuration management
with st.sidebar:
    st.markdown(f"""
    <div style="background-color:{COLORS['accent']}; padding:10px; border-radius:4px; margin-bottom:15px;">
        <h3 style="color:white; margin:0;">Configuration Management</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Add/remove configurations
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add Config", use_container_width=True):
            new_config = {
                'name': f"Config {len(st.session_state.configurations) + 1}",
                'pipe_thickness': 10.0,
                'pipe_diameter': 200.0,
                'pipe_length': 1000.0,
                'corrosion_length': 50.0,
                'corrosion_depth': 2.0,
                'yield_stress': 300.0,
                'uts': 400.0,
                'max_pressure': 10,
                'min_pressure': 5
            }
            st.session_state.configurations.append(new_config)
            st.session_state.active_config = len(st.session_state.configurations) - 1
            st.experimental_rerun()
    
    with col2:
        if st.button("🗑️ Remove Config", use_container_width=True, 
                    disabled=len(st.session_state.configurations) <= 1):
            if len(st.session_state.configurations) > 1:
                st.session_state.configurations.pop(st.session_state.active_config)
                st.session_state.active_config = min(st.session_state.active_config, 
                                                   len(st.session_state.configurations) - 1)
                st.experimental_rerun()
    
    # Configuration selector
    config_names = [f"{i+1}: {config['name']}" for i, config in enumerate(st.session_state.configurations)]
    selected_config = st.selectbox(
        "Select Configuration",
        options=config_names,
        index=st.session_state.active_config
    )
    st.session_state.active_config = config_names.index(selected_config)
    
    # Rename configuration
    current_config = st.session_state.configurations[st.session_state.active_config]
    new_name = st.text_input("Configuration Name", value=current_config['name'])
    current_config['name'] = new_name
    
    # Parameter inputs
    with st.expander("📏 Dimensional Parameters", expanded=True):
        current_config['pipe_thickness'] = st.number_input('Pipe Thickness (mm)', min_value=0.1, 
                                                         value=current_config['pipe_thickness'])
        current_config['pipe_diameter'] = st.number_input('Pipe Diameter (mm)', min_value=0.1, 
                                                        value=current_config['pipe_diameter'])
        current_config['corrosion_length'] = st.number_input('Corrosion Length (mm)', min_value=0.0, 
                                                           value=current_config['corrosion_length'])
        current_config['corrosion_depth'] = st.number_input('Corrosion Depth (mm)', min_value=0.0, max_value=10.0, 
                                                          value=current_config['corrosion_depth'])
    
    with st.expander("🧱 Material Properties", expanded=True):
        current_config['yield_stress'] = st.number_input('Yield Stress (MPa)', min_value=0.1, 
                                                       value=current_config['yield_stress'])
        current_config['uts'] = st.number_input('Ultimate Tensile Strength (MPa)', min_value=0.1, 
                                              value=current_config['uts'])
    
    with st.expander("📊 Operating Conditions", expanded=True):
        current_config['max_pressure'] = st.slider('Max Pressure (MPa)', 0, 50, 
                                                 current_config['max_pressure'])
        current_config['min_pressure'] = st.slider('Min Pressure (MPa)', 0, 50, 
                                                 current_config['min_pressure'])
    
    st.markdown("---")
    
    # Analysis controls
    if st.button('Run Analysis', use_container_width=True, type="primary"):
        st.session_state.run_analysis = True
    
    if st.button('Reset Analysis', use_container_width=True):
        st.session_state.run_analysis = False
    
    st.markdown(f"""
    <div style="background-color:{COLORS['accent']}; padding:10px; border-radius:4px; margin-top:15px;">
        <h4 style="color:white; margin:0;">Safety Indicators</h4>
        <p style="color:#e0e0e0; margin:0;">✅ Safe: Value ≤ 1<br>❌ Unsafe: Value > 1</p>
    </div>
    """, unsafe_allow_html=True)

# Image and intro section
st.subheader('Pipeline Configuration')
col1, col2 = st.columns([1, 2])
with col1:
    st.image("https://www.researchgate.net/profile/Changqing-Gong/publication/313456917/figure/fig1/AS:573308992266241@1513698923813/Schematic-illustration-of-the-geometry-of-a-typical-corrosion-defect.png", 
             caption="Fig. 1: Corrosion defect geometry")
with col2:
    st.markdown(f"""
    <div class="card">
        <h4>Assessment Protocol</h4>
        <ol>
            <li>Add configurations using the sidebar</li>
            <li>Enter parameters for each configuration</li>
            <li>Click "Run Analysis" to perform assessment</li>
            <li>Compare results across configurations</li>
            <li>Review burst pressure and fatigue results</li>
        </ol>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {'70%' if st.session_state.get('run_analysis', False) else '20%'};"></div>
        </div>
        <p style="text-align: right; margin:0; font-weight: bold;">
            Status: {'Analysis Complete' if st.session_state.get('run_analysis', False) else 'Ready for Input'}
        </p>
    </div>
    """, unsafe_allow_html=True)

# Engineering calculations
def calculate_pressures(inputs):
    t = inputs['pipe_thickness']
    D = inputs['pipe_diameter']
    Lc = inputs['corrosion_length']
    Dc = inputs['corrosion_depth']
    UTS = inputs['uts']
    
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
        'Von Mises': P_vm,
        'Tresca': P_tresca,
        'ASME B31G': P_asme,
        'DNV': P_dnv,
        'PCORRC': P_pcorrc
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
        'Max Stress': sigma_vm_max,
        'Min Stress': sigma_vm_min,
        'Alternating Stress': sigma_a,
        'Mean Stress': sigma_m,
        'Endurance Limit': Se,
        'Fatigue Strength': sigma_f
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
if st.session_state.get('run_analysis', False) and len(st.session_state.configurations) > 0:
    try:
        # Calculate all parameters for all configurations
        all_results = []
        for config in st.session_state.configurations:
            pressures = calculate_pressures(config)
            stresses = calculate_stresses(config)
            fatigue = calculate_fatigue_criteria(
                stresses['Alternating Stress'], stresses['Mean Stress'],
                stresses['Endurance Limit'], config['uts'], config['yield_stress'],
                stresses['Fatigue Strength']
            )
            
            all_results.append({
                'name': config['name'],
                'pressures': pressures,
                'stresses': stresses,
                'fatigue': fatigue,
                'config': config
            })
        
        # Configuration Comparison
        st.markdown(f"""
        <div class="section-header">
            <h3>Configuration Comparison</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create comparison table
        comparison_data = []
        for result in all_results:
            comparison_data.append({
                'Configuration': result['name'],
                'Burst Pressure (MPa)': f"{result['pressures']['ASME B31G']:.1f}",
                'Max Stress (MPa)': f"{result['stresses']['Max Stress']:.1f}",
                'Min Stress (MPa)': f"{result['stresses']['Min Stress']:.1f}",
                'Goodman': f"{result['fatigue']['Goodman']:.3f}",
                'Soderberg': f"{result['fatigue']['Soderberg']:.3f}",
                'Status': "✅ Safe" if result['fatigue']['Goodman'] <= 1 else "❌ Unsafe"
            })
        
        st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)
        
        # Burst Pressure Results
        st.markdown(f"""
        <div class="section-header">
            <h3>Burst Pressure Assessment</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Burst pressure bar chart
        fig, ax = plt.subplots(figsize=(10, 4))
        models = list(all_results[0]['pressures'].keys())
        width = 0.15
        x = np.arange(len(models))
        
        for i, result in enumerate(all_results):
            values = list(result['pressures'].values())
            ax.bar(x + (i * width), values, width, label=result['name'])
        
        ax.set_ylabel('Pressure (MPa)')
        ax.set_title('Burst Pressure by Model')
        ax.set_xticks(x + width * (len(all_results)-1)/2)
        ax.set_xticklabels(models)
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)
        
        # Stress Analysis
        st.markdown(f"""
        <div class="section-header">
            <h3>Stress Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Stress metrics table
            stress_data = []
            for result in all_results:
                stress_data.append({
                    'Config': result['name'],
                    'Max Stress': f"{result['stresses']['Max Stress']:.1f} MPa",
                    'Min Stress': f"{result['stresses']['Min Stress']:.1f} MPa",
                    'Alternating': f"{result['stresses']['Alternating Stress']:.1f} MPa",
                    'Mean': f"{result['stresses']['Mean Stress']:.1f} MPa"
                })
            st.dataframe(pd.DataFrame(stress_data), use_container_width=True)
        
        with col2:
            # Stress visualization
            fig, ax = plt.subplots(figsize=(8, 4))
            categories = ['Max Stress', 'Min Stress', 'Alternating Stress']
            
            for i, result in enumerate(all_results):
                values = [
                    result['stresses']['Max Stress'],
                    result['stresses']['Min Stress'],
                    result['stresses']['Alternating Stress']
                ]
                ax.plot(categories, values, 'o-', label=result['name'])
            
            ax.set_ylabel('Stress (MPa)')
            ax.set_title('Stress Distribution')
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            ax.legend()
            st.pyplot(fig)
        
        # Fatigue Assessment
        st.markdown(f"""
        <div class="section-header">
            <h3>Fatigue Assessment</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Fatigue criteria results
        fatigue_cols = st.columns(5)
        criteria = ['Goodman', 'Soderberg', 'Gerber', 'Morrow', 'ASME-Elliptic']
        colors = [COLORS['goodman'], COLORS['soderberg'], COLORS['gerber'], 
                 COLORS['morrow'], COLORS['asme']]
        
        for i, criterion in enumerate(criteria):
            with fatigue_cols[i]:
                st.markdown(f"<h4>{criterion}</h4>", unsafe_allow_html=True)
                for result in all_results:
                    value = result['fatigue'][criterion]
                    safe = value <= 1
                    status = "✅ Safe" if safe else "❌ Unsafe"
                    status_class = "safe" if safe else "unsafe"
                    
                    st.markdown(f"""
                    <div class="card">
                        <div><strong>{result['name']}</strong></div>
                        <div class="value-display">{value:.3f}</div>
                        <div class="{status_class}">{status}</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {min(100, value*100)}%; background-color: {colors[i]};"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Enhanced Fatigue Analysis Diagram
        st.markdown(f"""
        <div class="section-header">
            <h3>Fatigue Analysis Diagram</h3>
        </div>
        """, unsafe_allow_html=True)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate x-axis values
        max_uts = max([result['config']['uts'] for result in all_results])
        x = np.linspace(0, max_uts * 1.1, 100)
        
        # Plot all criteria with distinct colors
        ax.plot(x, all_results[0]['stresses']['Endurance Limit'] * (1 - x / max_uts), 
                color=COLORS['goodman'], linewidth=2, label='Goodman')
        ax.plot(x, all_results[0]['stresses']['Endurance Limit'] * (1 - x / all_results[0]['config']['yield_stress']), 
                color=COLORS['soderberg'], linewidth=2, label='Soderberg')
        ax.plot(x, all_results[0]['stresses']['Endurance Limit'] * (1 - (x / max_uts)**2), 
                color=COLORS['gerber'], linestyle='--', linewidth=2, label='Gerber')
        ax.plot(x, all_results[0]['stresses']['Endurance Limit'] * (1 - x / all_results[0]['stresses']['Fatigue Strength']), 
                color=COLORS['morrow'], linestyle=':', linewidth=2, label='Morrow')
        ax.plot(x, all_results[0]['stresses']['Endurance Limit'] * np.sqrt(1 - (x / all_results[0]['config']['yield_stress'])**2), 
                color=COLORS['asme'], linestyle='-.', linewidth=2, label='ASME-Elliptic')
        
        # Plot operating points for all configurations
        config_colors = plt.cm.tab10.colors
        for i, result in enumerate(all_results):
            ax.scatter(result['stresses']['Mean Stress'], result['stresses']['Alternating Stress'], 
                      color=config_colors[i], s=100, edgecolor='black', zorder=10,
                      label=f"{result['name']} (σm={result['stresses']['Mean Stress']:.1f}, σa={result['stresses']['Alternating Stress']:.1f})")
        
        # Formatting
        ax.set_xlim(0, max_uts * 1.1)
        ax.set_ylim(0, max([result['stresses']['Endurance Limit'] for result in all_results]) * 1.2)
        ax.set_xlabel('Mean Stress (σm) [MPa]', fontsize=10)
        ax.set_ylabel('Alternating Stress (σa) [MPa]', fontsize=10)
        ax.set_title('Fatigue Analysis Diagram', fontsize=12, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='upper right', fontsize=9)
        
        st.pyplot(fig)

    except Exception as e:
        st.error(f"🚨 An error occurred during analysis: {str(e)}")
else:
    st.markdown(f"""
    <div class="card">
        <h4 style="text-align: center;">⏳ Ready for Analysis</h4>
        <p style="text-align: center;">
            Configure your pipeline parameters and click 'Run Analysis'
        </p>
        <div class="progress-bar">
            <div class="progress-fill" style="width: 30%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# References section
st.markdown(f"""
<div class="section-header">
    <h3>References & Resources</h3>
</div>
""", unsafe_allow_html=True)

with st.expander("Research References", expanded=True):
    st.markdown("""
    - **ASME B31G-2012**  
      Manual for Determining the Remaining Strength of Corroded Pipelines
    - **DNV-RP-F101**  
      Corroded Pipelines Standard
    - **Xian-Kui Zhu** (2021)  
      *Journal of Pipeline Science and Engineering*  
      Comparative study of burst failure models for corroded pipelines
    """)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="background-color:{COLORS['accent']}; padding:15px; border-radius:5px; margin-top:30px;">
    <div style="display: flex; justify-content: space-between; align-items: center; color:white;">
        <div>
            <h4 style="margin:0;">FATIH v2.0 | Industrial Pipeline Integrity System</h4>
            <p style="margin:0; color:#e0e0e0;">© 2023 Engineering Solutions Ltd.</p>
        </div>
        <div style="text-align: right;">
            <p style="margin:0;">support@fatih-eng.com</p>
            <p style="margin:0;">+1 (800) 555-ENGI</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
