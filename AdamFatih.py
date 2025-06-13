import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from PIL import Image

#Configuration
st.set_page_config(layout="wide")

# Header
st.title("Assessment & Diagnostics for Aging Materials Fatigue Assessment Tool for Integrity and Health")

# Sidebar inputs
st.sidebar.header('User Input Parameters')

def user_input_features():
    params = {
        'pipe_thickness': st.sidebar.number_input('Pipe Thickness, t (mm)', min_value=0.1, value=10.0),
        'pipe_diameter': st.sidebar.number_input('Pipe Diameter, D (mm)', min_value=0.1, value=200.0),
        'pipe_length': st.sidebar.number_input('Pipe Length, L (mm)', min_value=0.1, value=1000.0),
        'corrosion_length': st.sidebar.number_input('Corrosion Length, Lc (mm)', min_value=0.0, value=50.0),
        'corrosion_depth': st.sidebar.number_input('Corrosion Depth, Dc (mm)', min_value=0.0, max_value=10.0, value=2.0),
        'yield_stress': st.sidebar.number_input('Yield Stress, Sy (MPa)', min_value=0.1, value=300.0),
        'uts': st.sidebar.number_input('Ultimate Tensile Strength, UTS (MPa)', min_value=0.1, value=400.0),
        'max_pressure': st.sidebar.slider('Maximum Operating Pressure, Pop, Max (MPa)', min_value=0, max_value=50, value=10),
        'min_pressure': st.sidebar.slider('Minimum Operating Pressure, Pop, Min (MPa)', min_value=0, max_value=50, value=5)
    }
    return params

# Image display
st.subheader('Dimensional Parameters')
st.image("https://www.researchgate.net/profile/Changqing-Gong/publication/313456917/figure/fig1/AS:573308992266241@1513698923813/Schematic-illustration-of-the-geometry-of-a-typical-corrosion-defect.png", 
         caption="Fig. 1: Schematic illustration of the geometry of a typical corrosion defect.")

# Get user inputs
inputs = user_input_features()

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

def calculate_stresses(inputs, pressures):
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
    sigma_f = UTS + 345
    
    # Fatigue criteria
    goodman = (sigma_a / Se) + (sigma_m / UTS)
    soderberg = (sigma_a / Se) + (sigma_m / Sy)
    gerber = (sigma_a / Se) + (sigma_m / UTS)**2
    morrow_allowable = Se * (1 - sigma_m / sigma_f)
    
    return {
        'sigma_vm_max': sigma_vm_max,
        'sigma_vm_min': sigma_vm_min,
        'sigma_a': sigma_a,
        'sigma_m': sigma_m,
        'Se': Se,
        'goodman': goodman,
        'soderberg': soderberg,
        'gerber': gerber,
        'morrow_allowable': morrow_allowable
    }

# Perform calculations
try:
    pressures = calculate_pressures(inputs)
    stresses = calculate_stresses(inputs, pressures)
    
    # Display results
    st.subheader('Input Parameters')
    st.dataframe(pd.DataFrame.from_dict(inputs, orient='index', columns=['Value']))
    
    st.subheader('Burst Pressure Calculations')
    pressure_df = pd.DataFrame.from_dict(pressures, orient='index', columns=['MPa'])
    st.dataframe(pressure_df.style.format("{:.2f}"))
    
    st.subheader('Stress Analysis')
    stress_df = pd.DataFrame({
        'Parameter': ['Max VM Stress', 'Min VM Stress', 'Alternating Stress', 'Mean Stress', 'Endurance Limit'],
        'Value (MPa)': [stresses['sigma_vm_max'], stresses['sigma_vm_min'], 
                        stresses['sigma_a'], stresses['sigma_m'], stresses['Se']]
    })
    st.dataframe(stress_df.style.format({"Value (MPa)": "{:.2f}"}))
    
    st.subheader('Fatigue Assessment')
    fatigue_df = pd.DataFrame({
        'Criterion': ['Goodman', 'Soderberg', 'Gerber', 'Morrow Allowable'],
        'Value': [stresses['goodman'], stresses['soderberg'], 
                 stresses['gerber'], stresses['morrow_allowable']],
        'Safe': [stresses['goodman'] <= 1, stresses['soderberg'] <= 1,
                stresses['gerber'] <= 1, stresses['sigma_a'] <= stresses['morrow_allowable']]
    })
    st.dataframe(fatigue_df.style.format({"Value": "{:.3f}"}))
    
# Plotting
st.subheader('Fatigue Analysis Diagram')
fig, ax = plt.subplots(figsize=(10, 8))

# Generate x-axis values
x = np.linspace(0, inputs['uts']*1.1, 100)

# Calculate all criteria lines
y_goodman = stresses['Se'] * (1 - x/inputs['uts'])
y_soderberg = stresses['Se'] * (1 - x/inputs['yield_stress'])
y_gerber = stresses['Se'] * (1 - (x/inputs['uts'])**2)
y_morrow = stresses['Se'] * (1 - x/(inputs['uts'] + 345))
y_asme = stresses['Se'] * np.sqrt(1 - (x/inputs['uts'])**2)

# Plot all criteria with distinct styles and LABELS
ax.plot(x, y_goodman, 'b-', linewidth=2, label='Goodman: σa/Se + σm/UTS = 1')
ax.plot(x, y_soderberg, 'r-', linewidth=2, label='Soderberg: σa/Se + σm/Sy = 1') 
ax.plot(x, y_gerber, 'g--', linewidth=2, label='Gerber: σa/Se + (σm/UTS)² = 1')
ax.plot(x, y_morrow, 'm:', linewidth=2, label='Morrow: σa/Se + σm/(UTS+345) = 1')
ax.plot(x, y_asme, 'c-.', linewidth=2, label='ASME-Elliptic: (σa/Se)² + (σm/Sy)² = 1')

# Plot operating point
ax.scatter(stresses['sigma_m'], stresses['sigma_a'], color='purple', s=120,
          label=f'Operating Point (σm={stresses["sigma_m"]:.1f}, σa={stresses["sigma_a"]:.1f})')

# Mark key points with their EQUATIONS
ax.scatter(0, stresses['Se'], color='green', s=100, 
          label=f'Se = {stresses["Se"]:.1f} MPa (Endurance Limit)')
ax.scatter(inputs['uts'], 0, color='blue', s=100, 
          label=f'UTS = {inputs["uts"]:.1f} MPa (Ultimate Strength)')
ax.scatter(inputs['yield_stress'], 0, color='red', s=100,
          label=f'Sy = {inputs["yield_stress"]:.1f} MPa (Yield Strength)')

# Formatting
ax.set_xlim(0, max(inputs['uts'], inputs['yield_stress'])*1.1)
ax.set_ylim(0, stresses['Se']*1.5)
ax.set_xlabel('Mean Stress (σm) [MPa]', fontsize=12)
ax.set_ylabel('Alternating Stress (σa) [MPa]', fontsize=12)
ax.set_title('Fatigue Analysis Diagram with All Criteria', fontsize=14)
ax.grid(True, linestyle=':', alpha=0.7)

# Improved legend with all criteria equations
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
plt.tight_layout()

st.pyplot(fig)

except ValueError as e:
    st.error(f"Calculation error: {str(e)}")
except Exception as e:
    st.error(f"An unexpected error occurred: {str(e)}")

# References and links
st.subheader('References')
st.markdown("""
- Xian-Kui Zhu, A comparative study of burst failure models for assessing remaining strength of corroded pipelines, 
  Journal of Pipeline Science and Engineering 1 (2021) 36-50, 
  [DOI:10.1016/j.jpse.2021.01.008](https://doi.org/10.1016/j.jpse.2021.01.008)
""")

st.subheader('Additional Resources')
st.markdown("""
- [Case Study](https://drive.google.com/file/d/1Ako5uVRPYL5k5JeEQ_Xhl9f3pMRBjCJv/view?usp=sharing)
- [Corroded Pipe Burst Data](https://docs.google.com/spreadsheets/d/1YJ7ziuc_IhU7-MMZOnRmh4h21_gf6h5Z/edit?gid=56754844#gid=56754844)
- [Pre-Test](https://forms.gle/wPvcgnZAC57MkCxN8)
- [Post-Test](https://forms.gle/FdiKqpMLzw9ENscA9)
""")
