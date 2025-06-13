import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configuration
st.set_page_config(layout="wide", page_title="Fatigue Analysis Tool")
st.title("Fatigue Analysis for Engineering Materials")

# Sidebar inputs
st.sidebar.header('Material Properties')
UTS = st.sidebar.number_input('Ultimate Tensile Strength (UTS) [MPa]', 
                             min_value=100.0, value=400.0, step=10.0)
Sy = st.sidebar.number_input('Yield Strength (Sy) [MPa]', 
                            min_value=50.0, value=300.0, step=10.0)
Se = st.sidebar.number_input('Endurance Limit (Se) [MPa]', 
                            min_value=10.0, value=200.0, step=10.0)

st.sidebar.header('Operating Stresses')
sigma_m = st.sidebar.number_input('Mean Stress (σm) [MPa]', 
                                 min_value=0.0, value=150.0, step=5.0)
sigma_a = st.sidebar.number_input('Alternating Stress (σa) [MPa]', 
                                 min_value=0.0, value=120.0, step=5.0)

# Calculate fatigue criteria values
sigma_f = UTS + 345  # Morrow's material constant

# Fatigue criteria calculations
goodman_val = (sigma_a / Se) + (sigma_m / UTS)
soderberg_val = (sigma_a / Se) + (sigma_m / Sy)
gerber_val = (sigma_a / Se) + (sigma_m / UTS)**2
morrow_val = (sigma_a / Se) + (sigma_m / sigma_f)
asme_val = np.sqrt((sigma_a / Se)**2 + (sigma_m / Sy)**2)  # Correct ASME-Elliptic using Sy

# Create the plot
fig, ax = plt.subplots(figsize=(10, 8))
x = np.linspace(0, max(UTS, Sy)*1.1, 200)

# Plot all criteria with proper equations
ax.plot(x, Se*(1 - x/UTS), 'b-', linewidth=2.5, 
        label=f'Goodman: σa/Se + σm/UTS = 1')
ax.plot(x, Se*(1 - x/Sy), 'r-', linewidth=2.5,
        label=f'Soderberg: σa/Se + σm/Sy = 1')
ax.plot(x, Se*(1 - (x/UTS)**2), 'g--', linewidth=2.5,
        label=f'Gerber: σa/Se + (σm/UTS)² = 1')
ax.plot(x, Se*(1 - x/sigma_f), 'm:', linewidth=2.5,
        label=f'Morrow: σa/Se + σm/(UTS+345) = 1')
ax.plot(x, Se*np.sqrt(1 - (x/Sy)**2), 'c-.', linewidth=2.5,
        label=f'ASME-Elliptic: (σa/Se)² + (σm/Sy)² = 1')

# Plot operating point
ax.scatter(sigma_m, sigma_a, color='purple', s=150, edgecolor='black', zorder=10,
          label=f'Operating Point (σm={sigma_m:.1f}, σa={sigma_a:.1f})')

# Mark key material points
ax.scatter(0, Se, color='green', s=100, label=f'Se = {Se:.1f} MPa (Endurance Limit)')
ax.scatter(UTS, 0, color='blue', s=100, label=f'UTS = {UTS:.1f} MPa (Ultimate Strength)')
ax.scatter(Sy, 0, color='red', s=100, label=f'Sy = {Sy:.1f} MPa (Yield Strength)')

# Formatting
max_x = max(UTS, Sy, sigma_m*1.2)
max_y = max(Se, sigma_a*1.5)
ax.set_xlim(0, max_x)
ax.set_ylim(0, max_y)
ax.set_xlabel('Mean Stress (σm) [MPa]', fontsize=12)
ax.set_ylabel('Alternating Stress (σa) [MPa]', fontsize=12)
ax.set_title('Fatigue Analysis Diagram with All Criteria', fontsize=14, fontweight='bold')
ax.grid(True, linestyle=':', alpha=0.7)

# Create a separate legend for material points
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='b', lw=2, label='Goodman'),
    Line2D([0], [0], color='r', lw=2, label='Soderberg'),
    Line2D([0], [0], color='g', linestyle='--', lw=2, label='Gerber'),
    Line2D([0], [0], color='m', linestyle=':', lw=2, label='Morrow'),
    Line2D([0], [0], color='c', linestyle='-.', lw=2, label='ASME-Elliptic'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='purple', 
           markersize=10, markeredgecolor='black', label='Operating Point'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='green', 
           markersize=8, label='Endurance Limit (Se)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', 
           markersize=8, label='Ultimate Strength (UTS)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
           markersize=8, label='Yield Strength (Sy)')
]

ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
plt.tight_layout()

# Display results
st.subheader('Fatigue Assessment Results')
col1, col2 = st.columns([1, 2])

with col1:
    results_df = pd.DataFrame({
        'Criterion': ['Goodman', 'Soderberg', 'Gerber', 'Morrow', 'ASME-Elliptic'],
        'Equation': [
            'σa/Se + σm/UTS = 1',
            'σa/Se + σm/Sy = 1',
            'σa/Se + (σm/UTS)² = 1',
            'σa/Se + σm/(UTS+345) = 1',
            '(σa/Se)² + (σm/Sy)² = 1'
        ],
        'Value': [goodman_val, soderberg_val, gerber_val, morrow_val, asme_val],
        'Safe': [goodman_val <= 1, soderberg_val <= 1, 
                gerber_val <= 1, morrow_val <= 1, asme_val <= 1]
    })
    results_df['Value'] = results_df['Value'].apply(lambda x: f"{x:.3f}")
    results_df['Safe'] = results_df['Safe'].apply(lambda x: "✅ Yes" if x else "❌ No")
    st.dataframe(results_df, height=300)

with col2:
    st.pyplot(fig)

# Explanations
st.subheader('Fatigue Criteria Explained')
st.markdown("""
- **Goodman Line:** Conservative for brittle materials
- **Soderberg Line:** Most conservative, suitable for high reliability
- **Gerber Parabola:** Better for ductile materials with mean stress
- **Morrow Line:** Accounts for mean stress effect using true fracture strength
- **ASME-Elliptic:** Most conservative criterion using both UTS and Sy
""")

# References
st.subheader('References')
st.markdown("""
- Shigley's Mechanical Engineering Design, 10th Ed.
- Norton, R. L. (2006). Machine Design: An Integrated Approach
- ASME Boiler and Pressure Vessel Code, Section VIII
""")

# Footer
st.markdown("---")
st.caption("Fatigue Analysis Tool v2.0 | Developed for Engineering Applications")
