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
    page_title="ADAM-FATIH",
    page_icon="⚙️"
)

# Color palette with high-contrast grayscale for diagrams
COLORS = {
    'Goodman': '#d62728',     # Red
    'Soderberg': '#1f77b4',   # Blue
    'Gerber': '#ff7f0e',      # Orange
    'Morrow': '#2ca02c',      # Green
    'ASME-Elliptic': '#9467bd', # Purple
    'OperatingPoint': '#FF0000', # Red (for visibility)
    'KeyPoints': '#000000'    # Black
}

# Dataset colors for the three operating points
DATASET_COLORS = ['#FF0000', '#00FF00', '#0000FF']  # Red, Green, Blue

# High-contrast color palette
BLACK = "#000000"
DARK_GRAY = "#333333"
MEDIUM_GRAY = "#666666"
LIGHT_GRAY = "#DDDDDD"
WHITE = "#FFFFFF"
ACCENT = "#444444"  # Dark gray for visual hierarchy
RED = "#FF0000"     # For critical indicators

# Custom CSS for high-contrast black and white styling
st.markdown(f"""
<style>
    /* Base styling for both themes */
    :root {{
        --primary-text: {BLACK};
        --secondary-text: {DARK_GRAY};
        --background: {WHITE};
        --card-bg: {WHITE};
        --border: {BLACK};
        --accent: {ACCENT};
        --light-gray: {LIGHT_GRAY};
    }}

    /* Apply to all text elements */
    body, .stApp, .stMarkdown, .stRadio, .stNumberInput, .stSelectbox, 
    .stSlider, .stButton, .stExpander, .stTable, .stDataFrame,
    .stAlert, .stProgress, .stCheckbox, .stTextInput, .stTextArea {{
        color: var(--primary-text) !important;
    }}

    /* Specific element overrides */
    .stRadio label, .stCheckbox label, .stSelectbox label, 
    .stNumberInput label, .stTextInput label, .stTextArea label,
    .stSlider label {{
        color: var(--primary-text) !important;
    }}

    /* Input fields */
    .stNumberInput input, .stTextInput input, .stTextArea textarea,
    .stSelectbox select {{
        background-color: var(--card-bg) !important;
        color: var(--primary-text) !important;
        border: 1px solid var(--border) !important;
    }}

    /* Tables */
    table, th, td {{
        color: var(--primary-text) !important;
        background-color: var(--card-bg) !important;
        border-color: var(--border) !important;
    }}

    /* Expanders */
    .stExpander > label {{
        color: var(--primary-text) !important;
        font-weight: bold !important;
    }}

    /* Main app container */
    .stApp {{
        background-color: var(--background);
        color: var(--primary-text);
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: var(--background);
        border-right: 1px solid var(--border);
    }}

    /* Cards and containers */
    .card, .material-card, .section-header {{
        background-color: var(--card-bg);
        color: var(--primary-text);
        border: 1px solid var(--border);
    }}

    /* Progress bars */
    .progress-container {{
        background-color: var(--light-gray);
    }}
    
    .progress-bar {{
        background-color: var(--border);
    }}

    /* Plot containers */
    .stPlot {{
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
    }}

    /* Force dark mode to use light colors */
    [data-theme="dark"] {{
        --primary-text: {BLACK} !important;
        --secondary-text: {DARK_GRAY} !important;
        --background: {WHITE} !important;
        --card-bg: {WHITE} !important;
        --border: {BLACK} !important;
        --accent: {ACCENT} !important;
        --light-gray: {LIGHT_GRAY} !important;
    }}

    /* Additional custom styles from original design */
    h1, h2, h3, h4, h5, h6 {{
        color: var(--primary-text) !important;
        border-bottom: 2px solid var(--border);
        padding-bottom: 0.3rem;
    }}
    
    .stButton>button {{
        background-color: {MEDIUM_GRAY};
        color: {WHITE};
        border-radius: 4px;
        border: 1px solid var(--border);
        font-weight: bold;
        padding: 0.5rem 1rem;
    }}
    
    .stButton>button:hover {{
        background-color: {DARK_GRAY};
        color: {WHITE};
    }}
    
    .value-display {{
        font-size: 1.6rem;
        font-weight: bold;
        color: var(--primary-text);
    }}
    
    .safe {{
        color: {MEDIUM_GRAY};
        font-weight: bold;
    }}
    
    .unsafe {{
        color: {RED};
        font-weight: bold;
    }}
    
    .dataset-tab.active {{
        background-color: var(--border);
        color: var(--background);
    }}
    
    .dataset-tab.inactive {{
        background-color: var(--light-gray);
        color: var(--primary-text);
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state for datasets
if 'datasets' not in st.session_state:
    st.session_state.datasets = {
        'Dataset 1': {'inputs': None, 'results': None},
        'Dataset 2': {'inputs': None, 'results': None},
        'Dataset 3': {'inputs': None, 'results': None}
    }

if 'current_dataset' not in st.session_state:
    st.session_state.current_dataset = 'Dataset 1'

# App header with high contrast theme
st.markdown(f"""
<div style="background-color:{WHITE}; padding:20px; border-radius:5px; margin-bottom:20px; border-bottom: 3px solid {BLACK}">
    <h1 style="color:{BLACK}; margin:0;">⚙️ Assessment & Diagnostics for Aging Materials Fatigue Assessment Tool for Integrity and Health (Adam-Fatih)</h1>
    <p style="color:{DARK_GRAY};">Pipeline Integrity Management System</p>
</div>
""", unsafe_allow_html=True)

# Dataset selection
st.markdown("### Dataset Selection")
current_dataset = st.radio(
    "Select dataset:",
    options=["Dataset 1", "Dataset 2", "Dataset 3"],
    index=["Dataset 1", "Dataset 2", "Dataset 3"].index(st.session_state.current_dataset),
    horizontal=True,
    label_visibility="collapsed"
)
st.session_state.current_dataset = current_dataset

# Sidebar with improved contrast headers
with st.sidebar:
    st.markdown(f"""
    <div style="background-color:{WHITE}; padding:10px; border-radius:4px; margin-bottom:15px; border: 1px solid {BLACK}">
        <h3 style="color:{BLACK}; margin:0;">Pipeline Parameters</h3>
        <p style="color:{BLACK}; margin:0;">Current: <strong>{st.session_state.current_dataset}</strong></p>
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
    <div style="background-color:{WHITE}; padding:10px; border-radius:4px; margin-top:15px; border: 1px solid {BLACK}">
        <h4 style="color:{BLACK}; margin:0;">Safety Indicators</h4>
        <p style="color:{MEDIUM_GRAY}; margin:0;">✅ Safe: Value ≤ 1<br>❌ Unsafe: Value > 1</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Run Analysis', use_container_width=True, type="primary"):
            st.session_state.run_analysis = True
            # Store inputs for current dataset
            st.session_state.datasets[st.session_state.current_dataset]['inputs'] = inputs
            # Clear results to force recalculation
            st.session_state.datasets[st.session_state.current_dataset]['results'] = None
    
    with col2:
        if st.button('Reset All', use_container_width=True):
            st.session_state.run_analysis = False
            # Reset all datasets
            for key in st.session_state.datasets:
                st.session_state.datasets[key] = {'inputs': None, 'results': None}

# Image and intro section
st.subheader('Pipeline Configuration')
col1, col2 = st.columns([1, 2])
with col1:
    st.image("https://www.researchgate.net/profile/Changqing-Gong/publication/313456917/figure/fig1/AS:573308992266241@1513698923813/Schematic-illustration-of-the-geometry-of-a-typical-corrosion-defect.png", 
             caption="Fig. 1: Corrosion defect geometry")
with col2:
    st.markdown(f"""
    <div class="material-card">
        <h4 style="border-bottom: 1px solid {BLACK}; padding-bottom: 5px;">Assessment Protocol</h4>
        <ol>
            <li>Select dataset to configure</li>
            <li>Enter pipeline dimensions and material properties</li>
            <li>Specify operating pressure range</li>
            <li>Click "Run Analysis" to perform assessment</li>
            <li>Review burst pressure calculations</li>
            <li>Analyze stress and fatigue results</li>
            <li>Compare multiple datasets on fatigue diagram</li>
        </ol>
        <div class="progress-container">
            <div class="progress-bar" style="width: {'50%' if st.session_state.get('run_analysis', False) else '10%'};"></div>
        </div>
        <p style="text-align: right; margin:0; color:{BLACK};">Status: {'Analysis Complete' if st.session_state.get('run_analysis', False) else 'Ready for Input'}</p>
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
    # Calculate for current dataset
    current_data = st.session_state.datasets[st.session_state.current_dataset]
    
    if current_data['inputs'] is not None:
        try:
            # Calculate all parameters
            pressures = calculate_pressures(current_data['inputs'])
            stresses = calculate_stresses(current_data['inputs'])
            fatigue = calculate_fatigue_criteria(
                stresses['sigma_a'], stresses['sigma_m'],
                stresses['Se'], current_data['inputs']['uts'], 
                current_data['inputs']['yield_stress'],
                stresses['sigma_f']
            )
            
            # Store results
            current_data['results'] = {
                'pressures': pressures,
                'stresses': stresses,
                'fatigue': fatigue
            }
            
            # Burst Pressure Results in Card Layout
            st.markdown(f"""
<div class="section-header">
    <h3 style="margin:0;">📊 Burst Pressure Assessment ({st.session_state.current_dataset})</h3>
</div>
""", unsafe_allow_html=True)
            
            burst_cols = st.columns(5)
            burst_data = [
                ("Von Mises", pressures['P_vm'], BLACK),
                ("Tresca", pressures['P_tresca'], MEDIUM_GRAY),
                ("ASME B31G", pressures['P_asme'], DARK_GRAY),
                ("DNV", pressures['P_dnv'], ACCENT),
                ("PCORRC", pressures['P_pcorrc'], BLACK)
            ]
            
            for i, (name, value, color) in enumerate(burst_data):
                with burst_cols[i]:
                    st.markdown(f"""
                    <div class="card" style="border-left: 4px solid {color};">
                        <h4 style="margin-top: 0;">{name}</h4>
                        <div class="value-display">{value:.2f} MPa</div>
                        <div style="height: 4px; background: {LIGHT_GRAY}; margin: 10px 0;">
                            <div style="height: 4px; background: {color}; width: {min(100, value/10*100)}%;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Stress Analysis
            st.markdown(f"""
<div class="section-header">
    <h3 style="margin:0;">📈 Stress Analysis ({st.session_state.current_dataset})</h3>
</div>
""", unsafe_allow_html=True)
            
            stress_col1, stress_col2 = st.columns([1, 1])
            
            with stress_col1:
                st.markdown(f"""
                <div class="material-card">
                    <h4>Stress Parameters</h4>
                    <table style="width:100%; border-collapse: collapse; font-size: 0.95rem;">
                        <tr style="border-bottom: 1px solid {BLACK};">
                            <td style="padding: 8px;">Max VM Stress</td>
                            <td style="text-align: right; padding: 8px; font-weight: bold;">{stresses['sigma_vm_max']:.2f} MPa</td>
                        </tr>
                        <tr style="border-bottom: 1px solid {BLACK};">
                            <td style="padding: 8px;">Min VM Stress</td>
                            <td style="text-align: right; padding: 8px; font-weight: bold;">{stresses['sigma_vm_min']:.2f} MPa</td>
                        </tr>
                        <tr style="border-bottom: 1px solid {BLACK};">
                            <td style="padding: 8px;">Alternating Stress</td>
                            <td style="text-align: right; padding: 8px; font-weight: bold;">{stresses['sigma_a']:.2f} MPa</td>
                        </tr>
                        <tr style="border-bottom: 1px solid {BLACK};">
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
                # Simple stress visualization with high contrast
                fig, ax = plt.subplots(figsize=(6, 4))
                categories = ['Max Stress', 'Min Stress', 'Amplitude']
                values = [
                    stresses['sigma_vm_max'],
                    stresses['sigma_vm_min'],
                    stresses['sigma_a']
                ]
                # Grayscale colors for bars
                colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Blue, Orange, Green
                bars = ax.bar(categories, values, color=colors, edgecolor=BLACK)
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f} MPa',
                            ha='center', va='bottom', fontsize=9, color=BLACK)
                
                ax.set_ylim(0, max(values) * 1.2)
                ax.set_title('Stress Distribution', fontsize=10, color=BLACK)
                ax.grid(axis='y', linestyle='--', alpha=0.7, color=MEDIUM_GRAY)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color(BLACK)
                ax.spines['bottom'].set_color(BLACK)
                ax.tick_params(axis='x', colors=BLACK)
                ax.tick_params(axis='y', colors=BLACK)
                ax.set_facecolor(WHITE)
                plt.tight_layout()
                st.pyplot(fig)
            
            # Fatigue Assessment with Safety Status
            st.markdown(f"""
<div class="section-header">
    <h3 style="margin:0;">🛡️ Fatigue Assessment ({st.session_state.current_dataset})</h3>
</div>
""", unsafe_allow_html=True)
            
            fatigue_cols = st.columns(5)
            fatigue_data = [
                ("Goodman", fatigue['Goodman'], "σa/Se + σm/UTS = 1", COLORS['Goodman']),
                ("Soderberg", fatigue['Soderberg'], "σa/Se + σm/Sy = 1", COLORS['Soderberg']),
                ("Gerber", fatigue['Gerber'], "σa/Se + (σm/UTS)² = 1", COLORS['Gerber']),
                ("Morrow", fatigue['Morrow'], "σa/Se + σm/(UTS+345) = 1", COLORS['Morrow']),
                ("ASME-Elliptic", fatigue['ASME-Elliptic'], "(σa/Se)² + (σm/Sy)² = 1", COLORS['ASME-Elliptic'])
            ]
            
            for i, (name, value, equation, color) in enumerate(fatigue_data):
                with fatigue_cols[i]:
                    safe = value <= 1
                    status = "✅ Safe" if safe else "❌ Unsafe"
                    status_class = "safe" if safe else "unsafe"
                    
                    st.markdown(f"""
                    <div class="card" style="border-left: 4px solid {color};">
                        <h4 style="margin-top: 0;">{name}</h4>
                        <div style="font-size: 0.85em; margin-bottom: 10px; color:{BLACK};">{equation}</div>
                        <div class="value-display">{value:.3f}</div>
                        <div class="{status_class}" style="margin-top: 10px;">{status}</div>
                        <div style="height: 4px; background: {LIGHT_GRAY}; margin: 10px 0;">
                            <div style="height: 4px; background: {color}; width: {min(100, value*100)}%;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Enhanced Plotting with Matplotlib with high contrast
            st.markdown(f"""
            <div class="section-header">
                <h3 style="margin:0;">📉 Fatigue Analysis Diagram (All Datasets)</h3>
            </div>
            """, unsafe_allow_html=True)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor(WHITE)
            
            # Generate x-axis values
            x = np.linspace(0, inputs['uts']*1.1, 100)
            
            # Plot all criteria with distinct grayscale and line styles
            ax.plot(x, stresses['Se']*(1 - x/inputs['uts']), 
                    color=COLORS['Goodman'], linewidth=2.5, linestyle='-', label='Goodman')
            ax.plot(x, stresses['Se']*(1 - x/inputs['yield_stress']), 
                    color=COLORS['Soderberg'], linewidth=2.5, linestyle='--', label='Soderberg')
            ax.plot(x, stresses['Se']*(1 - (x/inputs['uts'])**2), 
                    color=COLORS['Gerber'], linestyle=':', linewidth=2.5, label='Gerber')
            ax.plot(x, stresses['Se']*(1 - x/stresses['sigma_f']), 
                    color=COLORS['Morrow'], linestyle='-.', linewidth=2.5, label='Morrow')
            ax.plot(x, stresses['Se']*np.sqrt(1 - (x/inputs['yield_stress'])**2), 
                    color=COLORS['ASME-Elliptic'], linestyle=(0, (5, 1)), linewidth=2.5, label='ASME-Elliptic')
            
            # Plot operating points for all datasets
            markers = ['o', 's', 'D']  # Circle, Square, Diamond
            for i, (dataset_name, dataset) in enumerate(st.session_state.datasets.items()):
                if dataset['results']:
                    ds = dataset['results']['stresses']
                    ax.scatter(ds['sigma_m'], ds['sigma_a'], 
                              color=DATASET_COLORS[i], s=150, edgecolor='black', zorder=10,
                              marker=markers[i], label=f'{dataset_name} (σm={ds["sigma_m"]:.1f}, σa={ds["sigma_a"]:.1f})')
            
            # Mark key points with consistent style
            ax.scatter(0, stresses['Se'], color=COLORS['KeyPoints'], s=100, marker='o', 
                      label=f'Se = {stresses["Se"]:.1f} MPa')
            ax.scatter(inputs['uts'], 0, color=COLORS['KeyPoints'], s=100, marker='s', 
                      label=f'UTS = {inputs["uts"]:.1f} MPa')
            ax.scatter(inputs['yield_stress'], 0, color=COLORS['KeyPoints'], s=100, marker='^', 
                      label=f'Sy = {inputs["yield_stress"]:.1f} MPa')
            
            # Formatting with high contrast - handle incomplete datasets
            max_x = inputs['uts'] * 1.1
            max_y = stresses['Se'] * 1.5
            
            # Collect all operating points to determine axis limits
            all_points = []
            for dataset in st.session_state.datasets.values():
                if dataset['results']:
                    ds = dataset['results']['stresses']
                    all_points.append(ds['sigma_m'])
                    all_points.append(ds['sigma_a'])
            
            if all_points:
                max_x = max(max_x, max(all_points) * 1.2)
                max_y = max(max_y, max(all_points) * 1.5)
            
            ax.set_xlim(0, max_x)
            ax.set_ylim(0, max_y)
            ax.set_xlabel('Mean Stress (σm) [MPa]', fontsize=10, color=BLACK)
            ax.set_ylabel('Alternating Stress (σa) [MPa]', fontsize=10, color=BLACK)
            ax.set_title('Fatigue Analysis Diagram', fontsize=12, fontweight='bold', color=BLACK)
            ax.grid(True, linestyle='--', alpha=0.7, color=MEDIUM_GRAY)
            ax.set_facecolor(WHITE)
            
            # Set axis and tick colors to black
            ax.spines['bottom'].set_color(BLACK)
            ax.spines['top'].set_color(BLACK) 
            ax.spines['right'].set_color(BLACK)
            ax.spines['left'].set_color(BLACK)
            ax.tick_params(axis='x', colors=BLACK)
            ax.tick_params(axis='y', colors=BLACK)
            
            # Create custom legend
            ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1), fontsize=9, facecolor=WHITE, edgecolor=BLACK)
            plt.tight_layout()
            
            st.pyplot(fig)
            
            # Dataset comparison table
            st.markdown(f"""
            <div class="section-header">
                <h3 style="margin:0;">📋 Dataset Comparison</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Create comparison table
            comparison_data = []
            headers = ["Parameter", "Dataset 1", "Dataset 2", "Dataset 3"]
            
            # Add mean stress and alternating stress
            comparison_data.append(["Mean Stress (σm)", "", "", ""])
            comparison_data.append(["Alternating Stress (σa)", "", "", ""])
            
            # Add fatigue criteria
            for criterion in fatigue_data:
                comparison_data.append([criterion[0], "", "", ""])
            
            # Fill in values
            for i, dataset_name in enumerate(st.session_state.datasets.keys()):
                dataset = st.session_state.datasets[dataset_name]
                if dataset['results']:
                    stresses = dataset['results']['stresses']
                    fatigue = dataset['results']['fatigue']
                    
                    # Update values
                    comparison_data[0][i+1] = f"{stresses['sigma_m']:.2f} MPa"
                    comparison_data[1][i+1] = f"{stresses['sigma_a']:.2f} MPa"
                    
                    # Fatigue criteria
                    for j, criterion in enumerate(fatigue_data):
                        comparison_data[2+j][i+1] = f"{fatigue[criterion[0]]:.3f}"
                else:
                    # Show placeholder for incomplete datasets
                    comparison_data[0][i+1] = "N/A"
                    comparison_data[1][i+1] = "N/A"
                    for j in range(len(fatigue_data)):
                        comparison_data[2+j][i+1] = "N/A"
            
            # Display table
            html_table = "<table style='width:100%; border-collapse: collapse; border: 1px solid black;'>"
            html_table += "<tr style='background-color: #f2f2f2;'>"
            for header in headers:
                html_table += f"<th style='border: 1px solid black; padding: 8px;'>{header}</th>"
            html_table += "</tr>"
            
            for row_idx, row in enumerate(comparison_data):
                row_class = "background-color: #f9f9f9;" if row_idx % 2 == 0 else ""
                html_table += f"<tr style='{row_class}'>"
                for col_idx, cell in enumerate(row):
                    if col_idx == 0 and row_idx > 2:
                        # Make criterion names bold
                        html_table += f"<td style='border: 1px solid black; padding: 8px; font-weight: bold;'>{cell}</td>"
                    else:
                        html_table += f"<td style='border: 1px solid black; padding: 8px;'>{cell}</td>"
                html_table += "</tr>"
                
            html_table += "</table>"
            
            st.markdown(html_table, unsafe_allow_html=True)

        except ValueError as e:
            st.error(f"🚨 Calculation error: {str(e)}")
        except Exception as e:
            st.error(f"🚨 An unexpected error occurred: {str(e)}")
    else:
        st.warning("Please run analysis for this dataset first")
else:
    st.markdown(f"""
    <div class="material-card">
        <h4 style="text-align: center; color:{BLACK};">⏳ Ready for Analysis</h4>
        <p style="text-align: center; color:{BLACK};">
            Select a dataset, enter parameters in the sidebar, and click 'Run Analysis'
        </p>
        <div class="progress-container">
            <div class="progress-bar" style="width: 30%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# References and links in expanders
st.markdown(f"""
<div class="section-header">
    <h3 style="margin:0;">📚 References & Resources</h3>
</div>
""", unsafe_allow_html=True)

ref_col1, ref_col2 = st.columns([1, 1])
with ref_col1:
    with st.expander("Research References", expanded=True):
        st.markdown(f"""
        <div style="color:{BLACK};">
        - **Xian-Kui Zhu** (2021)  
          *Journal of Pipeline Science and Engineering*  
          Comparative study of burst failure models for corroded pipelines  
          [DOI:10.1016/j.jpse.2021.01.008](https://doi.org/10.1016/j.jpse.2021.01.008)
        
        - **ASME B31G-2012**  
          Manual for Determining the Remaining Strength of Corroded Pipelines
        
        - **DNV-RP-F101**  
          Corroded Pipelines Standard
        </div>
        """, unsafe_allow_html=True)

with ref_col2:
    with st.expander("Additional Resources", expanded=True):
        st.markdown(f"""
        <div style="color:{BLACK};">
        - [Case Study: Pipeline Failure Analysis](https://drive.google.com/file/d/1Ako5uVRPYL5k5JeEQ_Xhl9f3pMRBjCJv/view?usp=sharing)
        
        - [Corroded Pipe Burst Database](https://docs.google.com/spreadsheets/d/1YJ7ziuc_IhU7-MMZOnRmh4h21_gf6h5Z/edit?gid=56754844#gid=56754844)
        
        - [Pre-Assessment Questionnaire](https://forms.gle/wPvcgnZAC57MkCxN8)
        
        - [Post-Assessment Feedback](https://forms.gle/FdiKqpMLzw9ENscA9)
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="background-color:{LIGHT_GRAY}; padding:20px; border-radius:5px; margin-top:20px; border-top: 2px solid {BLACK}">
    <div style="display: flex; justify-content: space-between; align-items: center; color:{BLACK};">
        <div>
            <h4 style="margin:0;">FATIH v2.0 | Industrial Pipeline Integrity System</h4>
            <p style="margin:0;">© 2023 Engineering Solutions Ltd.</p>
        </div>
        <div style="text-align: right;">
            <p style="margin:0;">Technical Support: support@fatih-eng.com</p>
            <p style="margin:0;">Phone: +1 (800) 555-ENGI</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
