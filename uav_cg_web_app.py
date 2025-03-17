import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="UAV CG Analyzer", layout="wide")
st.title("🛩️ UAV Weight and Center of Gravity Analyzer")

# Material densities in kg/m^3
material_densities = {
    "Foam": 30,
    "Balsa Wood": 160,
    "Carbon Fiber": 1600,
    "Aluminum": 2700,
    "Titanium": 4500
}

# Select material
material = st.selectbox("Select Material for Structural Components:", list(material_densities.keys()))
density = material_densities[material]

# UAV Dimensions (meters)
fuselage_length = 1.0
fuselage_diameter = 0.2
wing_area = 0.5
wing_AR = 6
wing_span = np.sqrt(wing_area * wing_AR)
wing_chord = wing_area / wing_span

ht_area = 0.1
ht_AR = 4
ht_span = np.sqrt(ht_area * ht_AR)
ht_chord = ht_area / ht_span

vt_area = 0.05
vt_AR = 3
vt_height = np.sqrt(vt_area * vt_AR)
vt_chord = vt_area / vt_height

# Structural Volume Approximations
fuselage_volume = np.pi * (fuselage_diameter / 2)**2 * fuselage_length
wing_volume = wing_area * 0.01  # Thin airfoil assumption
vt_volume = vt_area * 0.01

# Structural Masses (kg)
fuselage_mass = fuselage_volume * density
wing_mass = wing_volume * density
vt_mass = vt_volume * density

# Payload Components (weights in grams)
payload = [
    {"name": "Camera", "weight": 125},
    {"name": "LiDAR", "weight": 50},
    {"name": "GPS", "weight": 76},
    {"name": "Comms", "weight": 50},
    {"name": "Battery", "weight": 559},
]

st.subheader("🔧 Adjust Component Positions (in meters)")

for comp in payload:
    col1, col2, col3 = st.columns(3)
    comp['x'] = col1.slider(f"{comp['name']} - X", 0.0, fuselage_length, 0.5, 0.01)
    comp['y'] = col2.slider(f"{comp['name']} - Y", -0.5, 0.5, 0.0, 0.01)
    comp['z'] = col3.slider(f"{comp['name']} - Z", 0.0, 0.5, 0.0, 0.01)
    comp['weight_kg'] = comp['weight'] / 1000

# Add structural components to total list
components = payload + [
    {"name": "Wing", "weight_kg": wing_mass, "x": fuselage_length / 2, "y": 0, "z": 0},
    {"name": "Fuselage", "weight_kg": fuselage_mass, "x": fuselage_length / 2, "y": 0, "z": 0},
    {"name": "Vertical Tail", "weight_kg": vt_mass, "x": fuselage_length * 0.9, "y": 0, "z": vt_height / 2}
]

# CG Calculation
W_total = sum(c['weight_kg'] for c in components)
cg_x = sum(c['x'] * c['weight_kg'] for c in components) / W_total
cg_y = sum(c['y'] * c['weight_kg'] for c in components) / W_total
cg_z = sum(c['z'] * c['weight_kg'] for c in components) / W_total

st.markdown(f"### 📍 Total Weight: **{W_total:.2f} kg**")
st.markdown(f"### 🎯 Center of Gravity (CG): **({cg_x:.2f}, {cg_y:.2f}, {cg_z:.2f}) m**")

# 3D Visualization
fig = go.Figure()

for comp in components:
    fig.add_trace(go.Scatter3d(
        x=[comp['x']], y=[comp['y']], z=[comp['z']],
        mode='markers+text',
        marker=dict(size=5, color='royalblue'),
        text=[comp['name']],
        textposition="top center",
        name=comp['name']
    ))

fig.add_trace(go.Scatter3d(
    x=[cg_x], y=[cg_y], z=[cg_z],
    mode='markers+text',
    marker=dict(size=6, color='red', symbol='x'),
    text=["CG"],
    textposition="bottom center",
    name="CG"
))

fig.add_trace(go.Scatter3d(
    x=[0, fuselage_length], y=[0, 0], z=[0, 0],
    mode='lines', line=dict(color='black', width=2), name="Fuselage"
))
fig.add_trace(go.Scatter3d(
    x=[fuselage_length / 2 - wing_span / 2, fuselage_length / 2 + wing_span / 2],
    y=[0, 0], z=[0, 0],
    mode='lines', line=dict(color='green', width=2), name="Wing"
))
fig.add_trace(go.Scatter3d(
    x=[fuselage_length * 0.9, fuselage_length * 0.9],
    y=[-ht_span / 2, ht_span / 2], z=[0, 0],
    mode='lines', line=dict(color='orange', width=2), name="Horizontal Tail"
))
fig.add_trace(go.Scatter3d(
    x=[fuselage_length * 0.9, fuselage_length * 0.9],
    y=[0, 0], z=[0, vt_height],
    mode='lines', line=dict(color='purple', width=2), name="Vertical Tail"
))

fig.update_layout(
    title="UAV Component Placement & CG",
    scene=dict(
        xaxis_title='X (m)',
        yaxis_title='Y (m)',
        zaxis_title='Z (m)',
        aspectmode='data',
        bgcolor='white'
    ),
    width=800,
    height=600,
    margin=dict(l=0, r=0, b=0, t=40)
)

st.plotly_chart(fig, use_container_width=True)
