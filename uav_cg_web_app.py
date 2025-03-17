import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Set page configuration
st.set_page_config(page_title="UAV CG Analyzer", layout="wide")
st.title("🛩️ UAV Weight and Center of Gravity Analyzer")

# ================== User Input Section for Weight Calculations ==================
st.sidebar.header("⚖️ Weight Calculation Parameters")

# Material properties
rho_mat = st.sidebar.number_input("Material Density (kg/m³)", value=2700.0, format="%.10f", help="Density of the material used (e.g., aluminum = 2700 kg/m³).")
# Load factor
n_ult = st.sidebar.number_input("Ultimate Load Factor (n_ult)", value=3.8, format="%.10f", help="Maximum load factor the UAV can withstand.")

# Wing parameters
wing_area = st.sidebar.number_input("Wing Area (m²)", value=0.5, format="%.10f", help="Total planform area of the wing.")
wing_AR = st.sidebar.number_input("Wing Aspect Ratio", value=6.0, format="%.10f", help="Aspect ratio of the wing (span² / area).")
wing_chord = st.sidebar.number_input("Wing Chord (m)", value=0.5, format="%.10f", help="Mean aerodynamic chord of the wing.")
t_c_max = st.sidebar.number_input("Max Thickness/Chord Ratio", value=0.12, format="%.10f", help="Maximum thickness-to-chord ratio of the wing.")
Lambda_0_25 = st.sidebar.number_input("Quarter-Chord Sweep Angle (degrees)", value=0.0, format="%.10f", help="Sweep angle at the quarter-chord line.")
lambda_ratio = st.sidebar.number_input("Wing Taper Ratio", value=1.0, format="%.10f", help="Ratio of tip chord to root chord.")
K_rho = st.sidebar.number_input("Material Density Factor (K_rho)", value=1.0, format="%.10f", help="Factor accounting for material density variations.")

# Fuselage parameters
fuselage_length = st.sidebar.number_input("Fuselage Length (m)", value=1.0, format="%.10f", help="Total length of the fuselage.")
fuselage_diameter = st.sidebar.number_input("Fuselage Diameter (m)", value=0.2, format="%.10f", help="Maximum diameter of the fuselage.")
K_inlet = st.sidebar.number_input("Inlet Factor (K_inlet)", value=1.0, format="%.10f", help="Factor accounting for inlet design.")

# Horizontal Tail parameters
ht_area = st.sidebar.number_input("Horizontal Tail Area (m²)", value=0.1, format="%.10f", help="Planform area of the horizontal tail.")
ht_AR = st.sidebar.number_input("Horizontal Tail Aspect Ratio", value=4.0, format="%.10f", help="Aspect ratio of the horizontal tail.")
ht_chord = st.sidebar.number_input("Horizontal Tail Chord (m)", value=0.1, format="%.10f", help="Mean aerodynamic chord of the horizontal tail.")
ht_t_c_max = st.sidebar.number_input("Horizontal Tail Max Thickness/Chord Ratio", value=0.12, format="%.10f", help="Maximum thickness-to-chord ratio of the horizontal tail.")
ht_Lambda_0_25 = st.sidebar.number_input("Horizontal Tail Quarter-Chord Sweep Angle (degrees)", value=0.0, format="%.10f", help="Sweep angle at the quarter-chord line of the horizontal tail.")
ht_lambda_ratio = st.sidebar.number_input("Horizontal Tail Taper Ratio", value=1.0, format="%.10f", help="Taper ratio of the horizontal tail.")

# Vertical Tail parameters
vt_area = st.sidebar.number_input("Vertical Tail Area (m²)", value=0.05, format="%.10f", help="Planform area of the vertical tail.")
vt_AR = st.sidebar.number_input("Vertical Tail Aspect Ratio", value=3.0, format="%.10f", help="Aspect ratio of the vertical tail.")
vt_chord = st.sidebar.number_input("Vertical Tail Chord (m)", value=0.05, format="%.10f", help="Mean aerodynamic chord of the vertical tail.")
vt_t_c_max = st.sidebar.number_input("Vertical Tail Max Thickness/Chord Ratio", value=0.12, format="%.10f", help="Maximum thickness-to-chord ratio of the vertical tail.")
vt_Lambda_0_25 = st.sidebar.number_input("Vertical Tail Quarter-Chord Sweep Angle (degrees)", value=0.0, format="%.10f", help="Sweep angle at the quarter-chord line of the vertical tail.")
vt_lambda_ratio = st.sidebar.number_input("Vertical Tail Taper Ratio", value=1.0, format="%.10f", help="Taper ratio of the vertical tail.")
V_v = st.sidebar.number_input("Vertical Tail Volume Coefficient", value=0.2, format="%.10f", help="Volume coefficient of the vertical tail.")
C_T = st.sidebar.number_input("Tail Cone Coefficient (C_T)", value=1.0, format="%.10f", help="Coefficient for the tail cone design.")
C_V = st.sidebar.number_input("Vertical Tail Coefficient (C_V)", value=1.0, format="%.10f", help="Coefficient for the vertical tail design.")


# Gravity
g = 9.81  # Gravity constant
# ================== Weight Calculation Functions ==================
def calculate_wing_weight():
    return (
        wing_area * wing_chord * t_c_max * rho_mat * K_rho * 
        ((wing_AR * n_ult) / np.cos(np.radians(Lambda_0_25))) ** 0.6 * 
        lambda_ratio ** 0.04 * g
    )

def calculate_fuselage_weight():
    return (
        fuselage_length * fuselage_diameter ** 2 * rho_mat * K_rho *
        n_ult ** 0.25 * K_inlet * g
    )


def calculate_horizontal_tail_weight():
    return (
        ht_area * ht_chord * ht_t_c_max * rho_mat * K_rho *
        ((ht_AR / np.cos(np.radians(ht_Lambda_0_25))) ** 0.6 *
        ht_lambda_ratio ** 0.04 * g
    )
    )

def calculate_vertical_tail_weight():
    return (
        vt_area * vt_chord * vt_t_c_max * rho_mat * K_rho *
        ((vt_AR / np.cos(np.radians(vt_Lambda_0_25))) ** 0.6 *
        vt_lambda_ratio ** 0.04 * V_v ** 0.2 * (C_T / C_V) ** 0.4 * g
    )
    )
# ================== Initialize Components ==================
if "components" not in st.session_state:
    st.session_state.components = [
        {"name": "Camera", "weight": 125, "x": 0.2, "y": 0, "z": 0.1, "weight_kg": 0.125},
        {"name": "LiDAR", "weight": 50, "x": 0.3, "y": 0, "z": 0.2, "weight_kg": 0.050},
        {"name": "GPS", "weight": 76, "x": 0.4, "y": 0, "z": 0.3, "weight_kg": 0.076},
        {"name": "Comms", "weight": 50, "x": 0.5, "y": 0, "z": 0.4, "weight_kg": 0.050},
        {"name": "Battery", "weight": 559, "x": 0.7, "y": 0, "z": 0.5, "weight_kg": 0.559},
        {"name": "Wing", "weight": 0, "x": 0.5, "y": 0, "z": 0.5, "weight_kg": 0},  # Placeholder
        {"name": "Fuselage", "weight": 0, "x": 0.5, "y": 0, "z": 0, "weight_kg": 0},  # Placeholder
        {"name": "Horizontal Tail", "weight": 0, "x": 0.5, "y": 0, "z": 0, "weight_kg": 0},  # Placeholder
        {"name": "Vertical Tail", "weight": 0, "x": 0.5, "y": 0, "z": 0, "weight_kg": 0},  # Placeholder
    ]

# ================== Update Component Weights ==================
def update_component_weights():
    # Recalculate weights
    wing_weight = calculate_wing_weight()
    fuse_weight = calculate_fuselage_weight()
    vt_weight = calculate_vertical_tail_weight()
    ht_weight = calculate_horizontal_tail_weight()

    # Update weights in session state
    for comp in st.session_state.components:
        if comp["name"] == "Wing":
            comp["weight"] = wing_weight * 1000
            comp["weight_kg"] = wing_weight
        elif comp["name"] == "Fuselage":
            comp["weight"] = fuse_weight * 1000
            comp["weight_kg"] = fuse_weight
        elif comp["name"] == "Horizontal Tail":
            comp["weight"] = ht_weight * 1000
            comp["weight_kg"] = ht_weight
        elif comp["name"] == "Vertical Tail":
            comp["weight"] = vt_weight * 1000
            comp["weight_kg"] = vt_weight

# Update weights whenever inputs change
update_component_weights()
# ================== Display Weight Calculations ==================
st.subheader("📝 Weight Calculations")

# Wing Weight Calculation
wing_weight = calculate_wing_weight()
st.markdown(f"**Wing Weight:**")
st.latex(rf"""
W_W = S_W \cdot MAC \cdot \left( \frac{{t}}{{C}} \right)_{{\max}} \cdot \rho_{{\text{{mat}}}} \cdot K_\rho \cdot \left( \frac{{\text{{AR}} \cdot n_{{\text{{ult}}}}}}{{\cos(\Lambda_{{0.25}})}} \right)^{{0.6}} \cdot \lambda^{{0.04}} \cdot g
""")
st.markdown(f"**Calculated Wing Weight:** {wing_weight:.2f} kg")

# Fuselage Weight Calculation
fuse_weight = calculate_fuselage_weight()
st.markdown(f"**Fuselage Weight:**")
st.latex(rf"""
W_F = L_f \cdot D^2_{{\max}} \cdot \rho_{{\text{{mat}}}} \cdot K_{{\rho_f}} \cdot n_{{\text{{ult}}}}^{{0.25}} \cdot K_{{\text{{inlet}}}} \cdot g
""")
st.markdown(f"**Calculated Fuselage Weight:** {fuse_weight:.2f} kg")

# Vertical Tail Weight Calculation
vt_weight = calculate_vertical_tail_weight()
st.markdown(f"**Vertical Tail Weight:**")
st.latex(rf"""
W_{{VT}} = S_{{VT}} \cdot MAC_{{VT}} \cdot \left( \frac{{t}}{{C}} \right)_{{\max \text{{VT}}}} \cdot \rho_{{\text{{mat}}}} \cdot K_{{\rho_{{VT}}}} \cdot \left( \frac{{\text{{AR}}_{{VT}}}}{{\cos(\Lambda_{{0.25_{{VT}}}})}} \right)^{{0.6}} \cdot \lambda^{{0.04}}_{{VT}} \cdot \bar{{V}}_V^{{0.2}} \left( \frac{{C_T}}{{C_V}} \right)^{{0.4}}
""")
st.markdown(f"**Calculated Vertical Tail Weight:** {vt_weight:.2f} kg")

# Horizontal Tail Weight Calculation
ht_weight = calculate_horizontal_tail_weight()
st.markdown(f"**Horizontal Tail Weight:**")
st.latex(rf"""
W_{{HT}} = S_{{HT}} \cdot MAC_{{HT}} \cdot \left( \frac{{t}}{{C}} \right)_{{\max \text{{HT}}}} \cdot \rho_{{\text{{mat}}}} \cdot K_{{\rho_{{HT}}}} \cdot \left( \frac{{\text{{AR}}_{{HT}}}}{{\cos(\Lambda_{{0.25_{{HT}}}})}} \right)^{{0.6}} \cdot \lambda^{{0.04}}_{{HT}} \cdot g
""")
st.markdown(f"**Calculated Horizontal Tail Weight:** {ht_weight:.2f} kg")
# ================== Adjust Component Positions and Weights ==================
def adjust_component_positions_and_weights(components):
    st.subheader("🔧 Adjust Component Positions and Weights")
    for i, comp in enumerate(components):
        st.write(f"### {comp['name']}")
        col1, col2, col3, col4, col5 = st.columns(5)
        comp['x'] = col1.number_input(f"{comp['name']} - X (m)", value=float(comp.get('x', 0.5)), step=0.01, key=f"x_{i}")
        comp['y'] = col2.number_input(f"{comp['name']} - Y (m)", value=float(comp.get('y', 0.0)), step=0.01, key=f"y_{i}")
        comp['z'] = col3.number_input(f"{comp['name']} - Z (m)", value=float(comp.get('z', 0.0)), step=0.01, key=f"z_{i}")
        comp['weight'] = col4.number_input(f"{comp['name']} - Weight (g)", value=float(comp.get('weight', 0)), step=1.0, key=f"weight_{i}")
        comp['weight_kg'] = comp['weight'] / 1000
        if col5.button(f"Remove {comp['name']}", key=f"remove_{i}"):
            components.pop(i)
            st.rerun()
    return components

# ================== Add New Component ==================
def add_component(components):
    st.subheader("➕ Add New Component")
    col1, col2, col3, col4 = st.columns(4)
    name = col1.text_input("Component Name", value="New Component")
    weight = col2.number_input("Weight (g)", value=100.0, step=1.0)
    x = col3.number_input("X (m)", value=0.5, step=0.01)
    y = col4.number_input("Y (m)", value=0.0, step=0.01)
    z = st.number_input("Z (m)", value=0.0, step=0.01)
    if st.button("Add Component"):
        components.append({
            "name": name,
            "weight": weight,
            "x": x,
            "y": y,
            "z": z,
            "weight_kg": weight / 1000
        })
        st.rerun()

# ================== Calculate CG ==================
def calculate_CG(components):
    W_total = sum(c['weight_kg'] for c in components)
    cg_x = sum(c['x'] * c['weight_kg'] for c in components) / W_total
    cg_y = sum(c['y'] * c['weight_kg'] for c in components) / W_total
    cg_z = sum(c['z'] * c['weight_kg'] for c in components) / W_total
    return W_total, cg_x, cg_y, cg_z

# ================== Adjust Components and Add New Ones ==================
st.session_state.components = adjust_component_positions_and_weights(st.session_state.components)
add_component(st.session_state.components)

# ================== Calculate and Display CG ==================
W_total, cg_x, cg_y, cg_z = calculate_CG(st.session_state.components)
st.markdown(f"### 📍 Total Weight: **{W_total:.2f} kg**")
st.markdown(f"### 🎯 Center of Gravity (CG): **({cg_x:.2f}, {cg_y:.2f}, {cg_z:.2f}) m**")

# ================== Derived Dimensions ==================
# Wing dimensions
wing_span = np.sqrt(wing_area * wing_AR)  # Wing span (m)
wing_chord = wing_area / wing_span  # Mean aerodynamic chord (m)

# Horizontal Tail dimensions
ht_span = np.sqrt(ht_area * ht_AR)  # Horizontal tail span (m)
ht_chord = ht_area / ht_span  # Mean aerodynamic chord (m)

# Vertical Tail dimensions
vt_height = np.sqrt(vt_area * vt_AR)  # Vertical tail height (m)
vt_chord = vt_area / vt_height  # Mean aerodynamic chord (m)

# ================== 3D Visualization ==================
fig = go.Figure()

# Fuselage cylinder
def create_fuselage(x_center, length, diameter):
    z = np.linspace(x_center - length / 2, x_center + length / 2, 50)
    theta = np.linspace(0, 2 * np.pi, 50)
    theta_grid, z_grid = np.meshgrid(theta, z)
    x_grid = diameter / 2 * np.cos(theta_grid) + x_center
    y_grid = diameter / 2 * np.sin(theta_grid)
    return x_grid, y_grid, z_grid

fuselage_x, fuselage_y, fuselage_z = create_fuselage(0.5, fuselage_length, fuselage_diameter)
fig.add_trace(go.Surface(
    x=fuselage_x, y=fuselage_y, z=fuselage_z,
    colorscale=[[0, 'gray'], [1, 'gray']],
    showscale=False,
    opacity=0.8,
    name="Fuselage"
))

# Wing mesh (z=0.5)
wing = next((c for c in st.session_state.components if c['name'] == "Wing"), None)
if wing:
    wing_x = [wing['x'] - wing_span / 2, wing['x'] + wing_span / 2]
    wing_y = [wing['y'] - wing_chord / 2, wing['y'] + wing_chord / 2]
    fig.add_trace(go.Mesh3d(
        x=[wing_x[0], wing_x[1], wing_x[1], wing_x[0]],
        y=[wing_y[0], wing_y[0], wing_y[1], wing_y[1]],
        z=[wing['z']] * 4,  # Now at z=0.5
        color='green',
        opacity=0.8,
        name="Wing"
    ))

# Horizontal Tail mesh (z=0)
ht = next((c for c in st.session_state.components if c['name'] == "Horizontal Tail"), None)
if ht:
    ht_x = [ht['x'] - ht_span / 2, ht['x'] + ht_span / 2]
    ht_y = [ht['y'] - ht_chord / 2, ht['y'] + ht_chord / 2]
    fig.add_trace(go.Mesh3d(
        x=[ht_x[0], ht_x[1], ht_x[1], ht_x[0]],
        y=[ht_y[0], ht_y[0], ht_y[1], ht_y[1]],
        z=[ht['z']] * 4,  # Now at z=0
        color='orange',
        opacity=0.8,
        name="Horizontal Tail"
    ))

# Vertical Tail mesh (z=0)
vt = next((c for c in st.session_state.components if c['name'] == "Vertical Tail"), None)
if vt:
    vt_x = [vt['x'] - vt_chord / 2, vt['x'] + vt_chord / 2]
    vt_z = [vt['z'] - vt_height / 2, vt['z'] + vt_height / 2]
    fig.add_trace(go.Mesh3d(
        x=[vt_x[0], vt_x[1], vt_x[1], vt_x[0]],
        y=[vt['y']] * 4,
        z=[vt_z[0], vt_z[0], vt_z[1], vt_z[1]],
        color='purple',
        opacity=0.8,
        name="Vertical Tail"
    ))

# Components and CG
for comp in st.session_state.components:
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

# ================== Results Table ==================
st.subheader("📊 Component Details and CG Contributions")
table_data = []
for comp in st.session_state.components:
    table_data.append({
        "Component": comp['name'],
        "Weight (kg)": f"{comp['weight_kg']:.2f}",
        "Position (x, y, z)": f"({comp['x']:.2f}, {comp['y']:.2f}, {comp['z']:.2f})",
        "CG Contribution": f"({comp['x'] * comp['weight_kg']:.2f}, {comp['y'] * comp['weight_kg']:.2f}, {comp['z'] * comp['weight_kg']:.2f})"
    })

# Add the TOTAL row
table_data.append({
    "Component": "TOTAL",
    "Weight (kg)": f"{W_total:.2f}",
    "Position (x, y, z)": "-",
    "CG Contribution": f"({cg_x:.2f}, {cg_y:.2f}, {cg_z:.2f})"  # Directly display CG coordinates
})

# Display the table
st.table(pd.DataFrame(table_data))
