import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

st.set_page_config(page_title="UAV CG & Weight Calculator", layout="wide")

st.title("🛩️ UAV Weight and CG Estimator")

# --- Material Selection ---
materials = {
    "Carbon Fiber": 1600,  # kg/m^3
    "Aluminum": 2700,
    "Foam": 100,
    "Plastic": 1200
}

selected_material = st.selectbox("Select Structural Material", list(materials.keys()))
density_structure = materials[selected_material]  # in kg/m^3

st.markdown("---")

# --- UAV Dimensions ---
Sw = 0.5     # Wing area (m^2)
AR = 6       # Wing aspect ratio
lambda_w = 0.7

Sht = 0.1    # Horizontal tail area (m^2)
ARht = 4     # Horizontal tail aspect ratio
lambda_ht = 0.5

Svt = 0.05   # Vertical tail area (m^2)
ARvt = 3     # Vertical tail aspect ratio
lambda_vt = 0.6

Lf = 1.0     # Fuselage length (m)
Df = 0.2     # Fuselage diameter (m)

# --- Component Weights ---
components = {
    "Camera": 125,
    "LiDAR Sensor": 50,
    "GPS Module": 76,
    "Communication Module": 50,
    "Battery": 559
}

# --- Component Placement Sliders ---
st.sidebar.title("📦 Component Placement (m)")
component_positions = {}
for name in components:
    x = st.sidebar.slider(f"{name} - x", 0.0, Lf, 0.5, step=0.01)
    y = st.sidebar.slider(f"{name} - y", -0.3, 0.3, 0.0, step=0.01)
    z = st.sidebar.slider(f"{name} - z", -0.3, 0.3, 0.0, step=0.01)
    component_positions[name] = {"x": x, "y": y, "z": z}

# --- Structural Weight Calculations ---
wing_span = np.sqrt(Sw * AR)
wing_volume = Sw * 0.02  # Assume 2 cm thickness
wing_weight = density_structure * wing_volume

ht_span = np.sqrt(Sht * ARht)
ht_volume = Sht * 0.015
ht_weight = density_structure * ht_volume

vt_height = np.sqrt(Svt * ARvt)
vt_volume = Svt * 0.015
vt_weight = density_structure * vt_volume

fuselage_volume = np.pi * (Df/2)**2 * Lf
fuselage_weight = density_structure * fuselage_volume

# --- Structural Component Positions ---
structure_components = {
    "Wing": {"weight": wing_weight * 1000, "x": 0.5, "y": 0.0, "z": 0.0},
    "Fuselage": {"weight": fuselage_weight * 1000, "x": 0.5, "y": 0.0, "z": 0.0},
    "Vertical Tail": {"weight": vt_weight * 1000, "x": 0.95, "y": 0.0, "z": 0.2},
    "Horizontal Tail": {"weight": ht_weight * 1000, "x": 0.95, "y": 0.0, "z": 0.1},
}

# --- Total Components ---
all_components = {}
all_components.update(structure_components)
for name, weight in components.items():
    all_components[name] = {
        "weight": weight,
        "x": component_positions[name]["x"],
        "y": component_positions[name]["y"],
        "z": component_positions[name]["z"]
    }

# --- CG Calculation ---
total_weight = sum(comp["weight"] for comp in all_components.values())
Xcg = sum(comp["weight"] * comp["x"] for comp in all_components.values()) / total_weight
Ycg = sum(comp["weight"] * comp["y"] for comp in all_components.values()) / total_weight
Zcg = sum(comp["weight"] * comp["z"] for comp in all_components.values()) / total_weight

# --- Display Results ---
st.subheader("📊 Results")
st.write(f"**Total Weight:** {total_weight:.2f} g")
st.write(f"**Center of Gravity (CG):** X = {Xcg:.2f} m, Y = {Ycg:.2f} m, Z = {Zcg:.2f} m")

# --- 3D Visualization ---
st.subheader("🧭 CG Location (3D View)")
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')

# Plot components
for name, comp in all_components.items():
    ax.scatter(comp["x"], comp["y"], comp["z"], label=name, s=comp["weight"] / 5, alpha=0.7)

# Plot CG
ax.scatter(Xcg, Ycg, Zcg, color='red', s=100, label="CG", marker='x')

# UAV Sketch
ax.plot([0.25, 0.75], [0, 0], [0, 0], 'black', lw=2)  # Wing
ax.plot([0.5, 0.5], [0, 0], [-0.1, 0.1], 'blue', lw=4)  # Fuselage (side view)
ax.plot([0.95, 0.95], [-ht_span/2, ht_span/2], [0.1, 0.1], 'green', lw=2)  # Horizontal tail
ax.plot([0.95, 0.95], [0, 0], [0.1, 0.3], 'purple', lw=2)  # Vertical tail

ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
ax.set_zlabel("Z (m)")
ax.set_title("UAV Structure & CG")
ax.legend()

st.pyplot(fig)
