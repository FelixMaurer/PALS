import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc
import matplotlib.patches as patches
import scipy.ndimage
import plotly.graph_objects as go

# --- App Configuration ---
st.set_page_config(page_title="Positron Annihilation Explorer", layout="wide")

st.title("Positron Annihilation in Polymers")
st.markdown("Explore the lifecycle of a positron, from its turbulent path through matter to the quantum rules of its decay, and the resulting PALS statistics.")

# --- Create Tabs for Step-by-Step Flow ---
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Path Through Matter", 
    "2. Positronium Formation", 
    "3. Decay Rules & Pick-Off", 
    "4. PALS Statistics"
])

# ==========================================
# TAB 1: Path Through Matter
# ==========================================
with tab1:
    st.header("Thermalization: The Path Through Matter")
    st.markdown("""
    When a high-energy positron is emitted into a polymer, it undergoes a series of rapid, inelastic collisions with the polymer chains. 
    It ionizes atoms and excites electrons, losing kinetic energy at each step until it reaches thermal equilibrium (thermalization). This erratic journey is known as a **random walk**.
    """)
    
    st.subheader("Simulated Positron Path (Random Walk)")
    steps = st.slider("Number of collision steps", min_value=100, max_value=5000, value=1000, step=100)
    
    np.random.seed(42)
    theta = np.random.uniform(0, 2*np.pi, steps)
    r = np.random.uniform(0, 1, steps) * np.exp(-np.linspace(0, 5, steps)) 
    
    x = np.cumsum(r * np.cos(theta))
    y = np.cumsum(r * np.sin(theta))
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, y, alpha=0.6, color='blue', label='Positron Path')
    ax.scatter(x[0], y[0], color='green', s=100, label='Emission Point', zorder=5)
    ax.scatter(x[-1], y[-1], color='red', s=100, label='Thermalization Point', zorder=5)
    ax.set_title("Positron Thermalization in a Polymer Matrix")
    ax.axis('off')
    ax.legend()
    st.pyplot(fig)

# ==========================================
# TAB 2: Positronium Formation
# ==========================================
with tab2:
    st.header("Step-by-Step: Localization & Positronium Formation")

    st.markdown("""
    ### Step 1: Seeking the Void (Localization)
    As the positron loses its kinetic energy and reaches thermal equilibrium, it must figure out where to "settle" within the polyacrylic matrix. Its final location is strictly dictated by the microscopic forces of the polymer.

    * **The Repulsive Landscape:** The molecular chains of a polymer consist of dense, positively charged atomic nuclei surrounded by tightly bound electron clouds. The positron experiences massive **Coulomb repulsion** from the positive atomic cores. Furthermore, as it begins interacting with the environment, it faces strong **exchange repulsion** (due to the Pauli exclusion principle) from the bulk electrons of the polymer chains.
    * **The Free Volume Cavity:** Because of this intense repulsion, the polymer chains act like towering mountains of high potential energy. Seeking the lowest possible energy state, the positron is naturally funneled away from the molecular backbone and pushed into the microscopic empty spaces—the **free volume cavities**. In amorphous polymers, these cavities are caused by realistic structural defects like inefficient chain packing, bulky side-groups, and terminating chain ends.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    # ---------------------------------------------------------
    # Generate Realistic Amorphous Polymer Chains
    # ---------------------------------------------------------
    np.random.seed(42)
    chain_segments = []
    points_x, points_y = [], []
    
    x_starts = np.linspace(0.5, 9.5, 14)
    
    for x_start in x_starts:
        curr_x = x_start
        segment_x, segment_y = [curr_x], [0.0]
        
        is_broken_chain = (3.5 < x_start < 6.5)
        
        for y in np.linspace(0.2, 10.0, 45):
            if is_broken_chain and (4.0 < y < 6.0):
                if len(segment_x) > 1:
                    chain_segments.append((segment_x, segment_y))
                segment_x, segment_y = [], [] 
                curr_x = x_start + np.random.normal(0, 0.3) 
                continue
                
            curr_x += np.random.normal(0, 0.12)
            
            dist_to_center = np.sqrt((curr_x - 5.0)**2 + (y - 5.0)**2)
            if dist_to_center < 1.6:
                angle = np.arctan2(y - 5.0, curr_x - 5.0)
                curr_x = 5.0 + 1.6 * np.cos(angle)
                
            segment_x.append(curr_x)
            segment_y.append(y)
            points_x.append(curr_x)
            points_y.append(y)
            
        if len(segment_x) > 1:
            chain_segments.append((segment_x, segment_y))

    # ---------------------------------------------------------
    # Compute Energy Landscape based on actual atomic nodes
    # ---------------------------------------------------------
    x_grid = np.linspace(0, 10, 100)
    y_grid = np.linspace(0, 10, 100)
    X, Y = np.meshgrid(x_grid, y_grid)
    Z = np.zeros_like(X)
    
    for px, py in zip(points_x, points_y):
        Z += 1.2 * np.exp(-((X - px)**2 + (Y - py)**2) / 0.25)
        
    Z += 0.5 
    Z = np.clip(Z, 0, 15) 
    
    min_idx = np.unravel_index(np.argmin(Z), Z.shape)
    cavity_x, cavity_y, cavity_z = X[min_idx], Y[min_idx], Z[min_idx]
    
    # ---------------------------------------------------------
    # PATH UPDATE: Positron now enters from the bottom
    # ---------------------------------------------------------
    path_t = np.linspace(0, 1, 25)
    start_x, start_y = 5.0, 0.5 # <-- Changed from 8.5, 5.0
    path_x = start_x + (cavity_x - start_x) * path_t
    path_y = start_y + (cavity_y - start_y) * path_t
    
    path_z = scipy.ndimage.map_coordinates(Z, [path_y * 10, path_x * 10], order=1) + 0.3

    # ==========================================
    # LEFT COLUMN: Physical Polymer Structure (Matplotlib)
    # ==========================================
    with col1:
        st.subheader("1. Amorphous Polymer Matrix")
        
        fig_struct, ax_struct = plt.subplots(figsize=(6, 6))
        
        for cx, cy in chain_segments:
            ax_struct.plot(cx, cy, '-', color='#4a69bd', alpha=0.7, linewidth=2.5)
            ax_struct.scatter(cx, cy, color='#4a69bd', s=15, zorder=3)

        ax_struct.plot(path_x, path_y, color='white', linestyle='--', linewidth=2.5, label="Positron Path")
        ax_struct.scatter(path_x[0], path_y[0], color='#2ed573', s=150, zorder=5, label="Thermalized Positron")
        ax_struct.scatter(cavity_x, cavity_y, color='#ff4757', s=250, marker='*', zorder=5, label="Trapped in Void")
        
        ax_struct.set_facecolor('#1e272e') 
        ax_struct.set_xlim(0, 10)
        ax_struct.set_ylim(0, 10)
        ax_struct.set_xlabel("X (nm)")
        ax_struct.set_ylabel("Y (nm)")
        ax_struct.legend(loc="lower left", facecolor='black', labelcolor='white', framealpha=0.7)
        
        st.pyplot(fig_struct)

    # ==========================================
    # RIGHT COLUMN: Computed Energy Landscape (Plotly Interactive)
    # ==========================================
    with col2:
        st.subheader("2. Resulting Energy Landscape")
        
        fig_loc = go.Figure()

        # 3D Surface
        fig_loc.add_trace(go.Surface(
            z=Z, x=x_grid, y=y_grid, 
            colorscale='Plasma', 
            opacity=0.9,
            colorbar=dict(title="Energy Barrier", len=0.5)
        ))

        # Positron Path
        fig_loc.add_trace(go.Scatter3d(
            x=path_x, y=path_y, z=path_z,
            mode='lines',
            line=dict(color='white', width=6, dash='dash'),
            name='Positron Path'
        ))

        # Start Point (Thermalized)
        fig_loc.add_trace(go.Scatter3d(
            x=[path_x[0]], y=[path_y[0]], z=[path_z[0]],
            mode='markers',
            marker=dict(color='#2ed573', size=8),
            name='Thermalized Positron'
        ))

        # End Point (Trapped)
        fig_loc.add_trace(go.Scatter3d(
            x=[cavity_x], y=[cavity_y], z=[cavity_z + 0.5],
            mode='markers',
            marker=dict(color='#ff4757', size=10, symbol='diamond'),
            name='Trapped in Void'
        ))

        # Formatting the Interactive Plot
        fig_loc.update_layout(
            height=750,  
            scene=dict(
                aspectratio=dict(x=1, y=1, z=1), 
                xaxis_title='X (nm)',
                yaxis_title='Y (nm)',
                zaxis_title='Energy (Repulsion)',
                xaxis=dict(range=[0, 10], showgrid=False),
                yaxis=dict(range=[0, 10], showgrid=False),
                zaxis=dict(range=[0, 15], showgrid=False), 
                camera=dict(
                    eye=dict(x=-1.5, y=-1.5, z=1.2)
                )
            ),
            margin=dict(l=0, r=0, b=0, t=0), 
            legend=dict(
                orientation="h",
                yanchor="bottom", y=0.95, 
                xanchor="right", x=1
            )
        )
        
        st.plotly_chart(fig_loc, use_container_width=True)

    st.markdown("""
    By comparing the physical matrix (left) to the computed energy landscape (right), you can clearly see how irregular polymer packing dictates the positron's destination. The positron is repelled by the dense ridges of the molecular backbone and naturally flows down into the deep, low-energy basin formed by the structural void. *(You can click and drag the 3D plot to rotate the energy landscape).*
    """)

    st.markdown("""
    As seen in the 3D landscape above, the positron avoids the bright yellow/orange peaks (the dense polyacrylic chains) and rolls down into the dark purple valley (the physical void). Once localized at the bottom of this potential energy well, it is ready for Step 2: forming Positronium.
    """)
# ==========================================
# STEP 2: Capturing a Partner (The Spur Model)
# ==========================================
st.header("Step 2: Capturing a Partner & Forming Positronium")

st.markdown(r"""
### The Ionization Track (Spur Model)
As the energetic positron ($e^+$) enters the polymer, it travels via a series of discrete **collisions**. At every collision point, the positron has enough energy to knock an electron ($e^-$) off a polymer molecule, leaving behind a heavy parent ion ($M^+$).

This sequence of events creates the **Spur**: a localized cluster of ions and electrons. Once the positron has scattered enough times to lose its kinetic energy (thermalize), it settles into a void and captures one of these nearby electrons via Coulomb attraction.
""")

# ---------------------------------------------------------
# 3D INTERACTIVE VISUALIZATION: Discrete Scattering Spur
# ---------------------------------------------------------
st.subheader("3D Visualization: Collision-Induced Ionization")

# 1. Generate a short, discrete 3D Random Walk (Fewer collisions)
np.random.seed(50)
n_collisions = 12
start_pos = np.array([10, -8, 8])
path = np.zeros((n_collisions, 3))
path[0] = start_pos

# Generate segments with a "pull" toward the void at [0,0,0]
for i in range(1, n_collisions):
    pull = -path[i-1] / np.linalg.norm(path[i-1]) * 2.5
    random_scatter = np.random.normal(0, 1.8, 3)
    path[i] = path[i-1] + random_scatter + pull

# 2. Place Ions (M+) and Electrons (e-) at EVERY collision point
# (Offsetting electrons slightly from the ions for visual clarity)
ions_x, ions_y, ions_z = path[:-1, 0], path[:-1, 1], path[:-1, 2]
electrons_x = ions_x + np.random.normal(0, 0.5, n_collisions-1)
electrons_y = ions_y + np.random.normal(0, 0.5, n_collisions-1)
electrons_z = ions_z + np.random.normal(0, 0.5, n_collisions-1)

# The final thermalized position and the specific electron to be captured
final_pos = path[-1]
captured_e = np.array([electrons_x[-1], electrons_y[-1], electrons_z[-1]])

fig_spur = go.Figure()

# --- 1. The Free Volume Void (Central Sphere) ---
u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
v_rad = 4.0
sphere_x = v_rad * np.cos(u) * np.sin(v)
sphere_y = v_rad * np.sin(u) * np.sin(v)
sphere_z = v_rad * np.cos(v)
fig_spur.add_trace(go.Mesh3d(x=sphere_x.flatten(), y=sphere_y.flatten(), z=sphere_z.flatten(), 
                             alphahull=0, opacity=0.1, color='cyan', name='Free Volume Void'))

# --- 2. The Positron Track (The Path) ---
fig_spur.add_trace(go.Scatter3d(x=path[:,0], y=path[:,1], z=path[:,2], 
                                mode='lines',
                                line=dict(color='white', width=4, dash='solid'), 
                                name='Positron Path ($e^+$)'))

# --- 3. Ionization Centers (M+) at every collision ---
fig_spur.add_trace(go.Scatter3d(x=ions_x, y=ions_y, z=ions_z, mode='markers',
                                marker=dict(color='#ffa502', size=6, symbol='x'), 
                                name='Ionization Center ($M^+$)'))

# --- 4. Spur Electrons (e-) scattered along the track ---
fig_spur.add_trace(go.Scatter3d(x=electrons_x[:-1], y=electrons_y[:-1], z=electrons_z[:-1], mode='markers',
                                marker=dict(color='#1e90ff', size=4, symbol='circle'), 
                                name='Spur Electrons ($e^-$)'))

# --- 5. The Final Capture (Ps Formation) ---
# Thermalized Positron (Red)
fig_spur.add_trace(go.Scatter3d(x=[final_pos[0]], y=[final_pos[1]], z=[final_pos[2]], mode='markers',
                                marker=dict(color='#ff4757', size=12), name='Thermalized $e^+$'))

# Captured Electron (Bright Blue)
fig_spur.add_trace(go.Scatter3d(x=[captured_e[0]], y=[captured_e[1]], z=[captured_e[2]], mode='markers',
                                marker=dict(color='#1e90ff', size=12, line=dict(color='white', width=2)), 
                                name='Captured $e^-$'))

# Attraction Force Vector
fig_spur.add_trace(go.Scatter3d(x=[final_pos[0], captured_e[0]], 
                                y=[final_pos[1], captured_e[1]], 
                                z=[final_pos[2], captured_e[2]],
                                mode='lines', line=dict(color='yellow', width=8), 
                                name='Coulomb Attraction'))

fig_spur.update_layout(
    height=750,
    scene=dict(
        xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
        aspectmode='cube',
        camera=dict(eye=dict(x=1.2, y=1.2, z=0.8))
    ),
    margin=dict(l=0, r=0, b=0, t=0),
    paper_bgcolor='rgba(0,0,0,0)',
    legend=dict(font=dict(color="white"), yanchor="top", y=0.95, xanchor="left", x=0.05)
)

st.plotly_chart(fig_spur, use_container_width=True)

# ---------------------------------------------------------
# EXISTING VISUALIZATION: Spin States (Corrected Syntax)
# ---------------------------------------------------------
col1, col2 = st.columns(2)

# Orbit logic for the 3D plots
theta = np.linspace(0, 2 * np.pi, 100)
orbit_x = np.cos(theta)
orbit_y = np.sin(theta)
orbit_z = np.zeros_like(theta)

def create_ps_figure(is_ortho):
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=orbit_x, y=orbit_y, z=orbit_z, mode='lines', line=dict(color='gray', dash='dash', width=3)))
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', marker=dict(size=4, color='white', symbol='cross')))
    
    # Positron
    fig.add_trace(go.Scatter3d(x=[1], y=[0], z=[0], mode='markers', marker=dict(size=14, color='#ff4757')))
    fig.add_trace(go.Scatter3d(x=[1, 1], y=[0, 0], z=[0, 0.8], mode='lines', line=dict(color='#ff4757', width=6)))
    fig.add_trace(go.Cone(x=[1], y=[0], z=[0.8], u=[0], v=[0], w=[0.5], sizeref=0.3, showscale=False, colorscale=[[0, '#ff4757'], [1, '#ff4757']]))

    # Electron
    z_end = 0.8 if is_ortho else -0.8
    cone_w = 0.5 if is_ortho else -0.5
    fig.add_trace(go.Scatter3d(x=[-1], y=[0], z=[0], mode='markers', marker=dict(size=14, color='#4a69bd')))
    fig.add_trace(go.Scatter3d(x=[-1, -1], y=[0, 0], z=[0, z_end], mode='lines', line=dict(color='#4a69bd', width=6)))
    fig.add_trace(go.Cone(x=[-1], y=[0], z=[z_end], u=[0], v=[0], w=[cone_w], sizeref=0.3, showscale=False, colorscale=[[0, '#4a69bd'], [1, '#4a69bd']]))

    fig.update_layout(
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), camera=dict(eye=dict(x=0, y=-1.8, z=0.6))),
        height=350, margin=dict(l=0, r=0, b=0, t=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

with col1:
    st.subheader("Para-Positronium (p-Ps)")
    st.plotly_chart(create_ps_figure(is_ortho=False), use_container_width=True)
    st.markdown(r"""
    * **Spin Alignment:** Anti-parallel ($\uparrow \downarrow$)
    * **Total Spin:** $S = 0$ (Singlet)
    * **Formation Probability:** 25%
    * **Vacuum Lifetime:** ~0.125 ns
    
    The opposite spins allow for rapid self-annihilation. It disappears almost instantly, making it a poor probe for cavity size.
    """)

with col2:
    st.subheader("Ortho-Positronium (o-Ps)")
    st.plotly_chart(create_ps_figure(is_ortho=True), use_container_width=True)
    st.markdown(r"""
    * **Spin Alignment:** Parallel ($\uparrow \uparrow$)
    * **Total Spin:** $S = 1$ (Triplet)
    * **Formation Probability:** 75%
    * **Vacuum Lifetime:** ~142 ns
    
    The parallel spins forbid simple two-photon decay. Its **extended lifetime** allows it to bounce off cavity walls thousands of times, becoming our "measuring stick."
    """)
st.markdown("""
### Step 3: The Rules of Spin
Both the electron and the positron are fermions, meaning they each possess an intrinsic angular momentum, or "spin", of $s = 1/2$. When these two particles bind together, quantum mechanics dictates that their spins must combine. 

Because spin is a vector, these two $1/2$ spins can either point in opposite directions (canceling out) or point in the same direction (adding together). This creates two fundamentally different "species" of Positronium.
""")

st.divider()
st.markdown("### Step 4: The Two Quantum States (Singlet vs. Triplet)")

# Quantum Parameters Comparison
col1, col2 = st.columns(2)
with col1:
    st.info("""
    ### Para-Positronium (p-Ps)
    **The Singlet State**
    
    When the spins are anti-parallel, they cancel each other out. There is only one unique mathematical way for this to happen, hence the name "Singlet".
    
    * **Spin Alignment:** Anti-Parallel ($\\uparrow \\downarrow$)
    * **Total Spin ($S$):** $1/2 - 1/2 = 0$
    * **Magnetic Quantum Number ($m_s$):** 0
    * **Orbital Angular Momentum ($L$):** 0 (Ground state)
    * **Parity ($P = (-1)^{L+1}$):** -1 (Odd)
    * **Charge Parity ($C = (-1)^{L+S}$):** +1 (Even)
    * **Vacuum Lifetime:** ~125 ps
    * **Formation Probability:** 25% (1 out of 4 possible spin states)
    """)
with col2:
    st.warning("""
    ### Ortho-Positronium (o-Ps)
    **The Triplet State**
    
    When the spins are parallel, they add up. Because a total spin of 1 can orient itself in three different ways relative to an external axis (down, flat, or up), it is called a "Triplet".
    
    * **Spin Alignment:** Parallel ($\\uparrow \\uparrow$)
    * **Total Spin ($S$):** $1/2 + 1/2 = 1$
    * **Magnetic Quantum Number ($m_s$):** -1, 0, or +1
    * **Orbital Angular Momentum ($L$):** 0 (Ground state)
    * **Parity ($P = (-1)^{L+1}$):** -1 (Odd)
    * **Charge Parity ($C = (-1)^{L+S}$):** -1 (Odd)
    * **Vacuum Lifetime:** ~142 ns
    * **Formation Probability:** 75% (3 out of 4 possible spin states)
    """)

st.divider()
st.markdown("""
### Step 5: Hyperfine Splitting
Because the electron and positron are spinning, they act like tiny bar magnets. In the Triplet state (o-Ps), the "magnets" are aligned, which creates a slightly repulsive magnetic interaction. In the Singlet state (p-Ps), the opposite alignment is magnetically attractive. 

This magnetic spin-spin interaction causes a slight difference in their energy levels, known as **Hyperfine Splitting**. Ortho-positronium sits at a slightly higher energy level than para-positronium.
""")

fig_ps, (ax_split, ax_spin) = plt.subplots(1, 2, figsize=(12, 5))

# Left Panel: Energy Splitting
ax_split.set_title("Hyperfine Energy Splitting")
ax_split.axis('off')
ax_split.set_xlim(0, 5)
ax_split.set_ylim(-1, 3)

# Energy levels
ax_split.hlines(0, 1, 2, color='black', linestyles='dashed')
ax_split.text(0.5, 0, "Unperturbed\nGround State", va='center')

ax_split.hlines(1.5, 3, 4, color='orange', linewidth=3)
ax_split.text(4.2, 1.5, "Triplet (o-Ps)\nS=1", va='center')

ax_split.hlines(-0.5, 3, 4, color='blue', linewidth=3)
ax_split.text(4.2, -0.5, "Singlet (p-Ps)\nS=0", va='center')

# Splitting lines
ax_split.plot([2, 3], [0, 1.5], 'k--', alpha=0.5)
ax_split.plot([2, 3], [0, -0.5], 'k--', alpha=0.5)

# Energy difference text
ax_split.annotate(r'$\Delta E \approx 8.4 \times 10^{-4}$ eV', xy=(3.5, 0.5), ha='center', color='red', fontsize=10)

# Right Panel: Spin Alignment Sketch
ax_spin.set_title("Spin Alignments in Ground State")
ax_spin.axis('off')
ax_spin.set_xlim(-2, 2)
ax_spin.set_ylim(-2, 2)

# Para
ax_spin.text(-1, 1.2, "Para-Ps (Anti-Parallel)", ha='center', fontweight='bold')
ax_spin.plot(-1.3, 0, 'ro', markersize=20, alpha=0.7) # Positron
ax_spin.plot(-0.7, 0, 'bo', markersize=20, alpha=0.7) # Electron
ax_spin.arrow(-1.3, -0.3, 0, 0.6, head_width=0.1, color='black', lw=2) # Spin Up
ax_spin.arrow(-0.7, 0.3, 0, -0.6, head_width=0.1, color='black', lw=2) # Spin Down

# Ortho
ax_spin.text(1, 1.2, "Ortho-Ps (Parallel)", ha='center', fontweight='bold')
ax_spin.plot(0.7, 0, 'ro', markersize=20, alpha=0.7) # Positron
ax_spin.plot(1.3, 0, 'bo', markersize=20, alpha=0.7) # Electron
ax_spin.arrow(0.7, -0.3, 0, 0.6, head_width=0.1, color='black', lw=2) # Spin Up
ax_spin.arrow(1.3, -0.3, 0, 0.6, head_width=0.1, color='black', lw=2) # Spin Up

st.pyplot(fig_ps)

# ==========================================
# TAB 3: The Triplet State (Decay Rules)
# ==========================================
with tab3:
    st.header("Charge Parity & The Forbidden Decay")
    
    st.markdown("""
    In quantum mechanics, when particles annihilate into photons, a property called **Charge Parity (C-parity)** must be conserved. 
    A single photon has a C-parity of $-1$. Therefore, an event producing $n$ photons has a total C-parity of $(-1)^n$.
    """)
    
    st.latex(r"C_{\text{Positronium}} = (-1)^{L+S}")
    
    st.markdown("""
    * **Para-Ps ($S=0$):** $C = (-1)^{0+0} = +1$. It can easily decay into **2 photons** ($(-1)^2 = +1$).
    * **Ortho-Ps ($S=1$):** $C = (-1)^{0+1} = -1$. It *must* decay into an odd number of photons. 
    
    **Why not 1 photon?** A system at rest cannot emit a single photon without violating the conservation of momentum. Therefore, isolated ortho-positronium is forced to decay into **3 photons**, which is mathematically highly improbable and takes a very long time (~142 ns).
    """)
    
    st.divider()
    st.header("The Pick-Off Loophole in Matter")
    st.markdown("""
    When o-Ps is trapped inside a polymer cavity, it doesn't wait 142 ns to decay. As it bounces around, its outer positron penetrates the electron clouds of the polymer chains lining the cavity wall. 
    
    If the positron encounters a polymer electron with an **opposite spin** to its own, it abandons its original partner, forms a temporary pseudo-singlet state with the wall electron, and instantly annihilates via the much faster 2-photon pathway. This is called **Pick-Off Annihilation**.
    """)
    
    fig_decay, (ax_vac, ax_wall) = plt.subplots(1, 2, figsize=(12, 6))
    
    # --- Left Panel: Vacuum Decay (3 photons) ---
    ax_vac.set_title("Direct Vacuum Decay: 3 Photons (Slow)")
    ax_vac.axis('off')
    ax_vac.set_xlim(-2, 2)
    ax_vac.set_ylim(-2, 2)
    
    # Draw o-Ps
    ax_vac.plot(0, 0, 'ro', markersize=12, label='Positron')
    ax_vac.plot(0.2, 0.2, 'bo', markersize=12, label='Electron')
    ax_vac.text(0, -0.4, "o-Ps (Total Spin=1)", ha='center')
    
    # Draw 3 Photons
    angles = [np.pi/2, 7*np.pi/6, 11*np.pi/6]
    for angle in angles:
        x_w = [0.2 + i*0.2*np.cos(angle) for i in range(8)]
        y_w = [0.2 + i*0.2*np.sin(angle) + 0.05*np.sin(i*np.pi) for i in range(8)]
        ax_vac.plot(x_w, y_w, 'y-', lw=2)
    ax_vac.text(1, 1, r"$\gamma$", color='goldenrod', fontsize=16)
    ax_vac.text(-1.5, -0.5, r"$\gamma$", color='goldenrod', fontsize=16)
    ax_vac.text(1, -1.5, r"$\gamma$", color='goldenrod', fontsize=16)
    ax_vac.legend(loc='upper left', fontsize='small')
    
    # --- Right Panel: Pick-off in matter ---
    ax_wall.set_title("Pick-Off in Matter: 2 Photons (Fast)")
    ax_wall.axis('off')
    ax_wall.set_xlim(-2, 2)
    ax_wall.set_ylim(-2, 2)
    
    # Polymer Wall
    rect = patches.Rectangle((0.5, -2), 1.5, 4, linewidth=1, edgecolor='none', facecolor='lightgray', alpha=0.5)
    ax_wall.add_patch(rect)
    ax_wall.text(1.25, 1.5, "Polymer Wall\n(Dense Electrons)", ha='center')
    
    # Path of o-Ps
    ax_wall.plot([-1.5, 0.5], [0, 0], 'k--', lw=1)
    ax_wall.plot(-1.5, 0, 'go', markersize=8) # Start point
    ax_wall.text(-1.5, 0.2, "Trapped\no-Ps", ha='center')
    
    # Original o-Ps pair
    ax_wall.plot(0.5, 0, 'ro', markersize=12) # Positron hits wall
    ax_wall.plot(0.3, -0.2, 'bo', markersize=12, alpha=0.3) # Original electron left behind
    ax_wall.arrow(0.5, 0.2, 0, 0.3, head_width=0.08, color='red') # Positron spin up
    
    # Pick-off electron from wall
    ax_wall.plot(0.7, 0, 'bo', markersize=12) 
    ax_wall.arrow(0.7, 0.5, 0, -0.3, head_width=0.08, color='blue') # Wall electron spin down
    
    # 2 Photons emitted
    x_w1 = [0.6 + i*0.2*np.cos(np.pi/4) for i in range(6)]
    y_w1 = [0 + i*0.2*np.sin(np.pi/4) + 0.05*np.sin(i*np.pi) for i in range(6)]
    ax_wall.plot(x_w1, y_w1, 'y-', lw=2)
    
    x_w2 = [0.6 + i*0.2*np.cos(5*np.pi/4) for i in range(6)]
    y_w2 = [0 + i*0.2*np.sin(5*np.pi/4) + 0.05*np.sin(i*np.pi) for i in range(6)]
    ax_wall.plot(x_w2, y_w2, 'y-', lw=2)
    
    ax_wall.text(1.5, 1, r"$\gamma$", color='goldenrod', fontsize=16)
    ax_wall.text(-0.5, -1, r"$\gamma$", color='goldenrod', fontsize=16)
    
    st.pyplot(fig_decay)

# ==========================================
# TAB 4: PALS Statistics
# ==========================================
with tab4:
    st.header("PALS Statistics: Multi-Component Spectra")
    st.markdown("""
    Positron Annihilation Lifetime Spectroscopy (PALS) measures the time difference between the positron's emission and its annihilation. Because there are different decay pathways, the resulting statistical spectrum is a combination of several exponential decays convolved with the detector's timing resolution.
    """)
    
    st.latex(r"N(t) = B + \sum_{i=1}^{k} A_i \exp\left(-\frac{t-t_0}{\tau_i}\right) \text{erfc}\left( \frac{1}{\sqrt{2}} \left( \frac{\sigma}{\tau_i} - \frac{t-t_0}{\sigma} \right) \right)")
    
    st.markdown("""
    When building mathematical models to fit these spectra, navigating the parameter space can be difficult. In specialized optimization routines, rather than varying all individual parameters freely, it is often much more robust to optimize for only the ratio between specific component states (such as the ratio between the M0 and M2 components). 
    
    Furthermore, when correlating these lifetimes to physical polymer structures, keeping other matrix properties constant so that only the repulsion is changed allows researchers to cleanly observe how atomic repulsive forces directly dictate cavity size and o-Ps pick-off rates.
    """)
    
    st.subheader("Simulated Multi-Component Spectrum (Realistic Instrument Resolution)")
    
    # Generate Realistic PALS Data
    x_data = np.linspace(12, 25, 1000)
    sigma = 0.297 / 2.35 
    t0 = 13.5 
    
    # Components
    A1, tau1 = 25000, 0.25  # p-Ps
    A2, tau2 = 1700, 0.61   # Free positron
    A3, tau3 = 350, 1.68    # o-Ps pick-off
    B = 2.0                 # Background noise
    
    # Calculate convoluted decays
    comp1 = A1 * np.exp(-(x_data-t0)/tau1) * erfc(1/np.sqrt(2) * (sigma/tau1 - (x_data-t0)/sigma))
    comp2 = A2 * np.exp(-(x_data-t0)/tau2) * erfc(1/np.sqrt(2) * (sigma/tau2 - (x_data-t0)/sigma))
    comp3 = A3 * np.exp(-(x_data-t0)/tau3) * erfc(1/np.sqrt(2) * (sigma/tau3 - (x_data-t0)/sigma))
    
    total_decay = comp1 + comp2 + comp3 + B
    
    np.random.seed(42)
    noisy_decay = np.random.poisson(np.maximum(total_decay, 0))
    
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.plot(x_data, noisy_decay, '.', color='black', alpha=0.3, label='Raw Data (Counts)')
    ax2.plot(x_data, total_decay, 'r-', linewidth=2, label='Total Fit Model')
    ax2.plot(x_data, comp1, '--', label=f'Component 1: p-Ps (~{tau1*1000:.0f} ps)')
    ax2.plot(x_data, comp2, '--', label=f'Component 2: Free e+ (~{tau2*1000:.0f} ps)')
    ax2.plot(x_data, comp3, '--', label=f'Component 3: o-Ps Pick-off (~{tau3:.2f} ns)')
    
    ax2.set_yscale('log')
    ax2.set_xlabel('Time (ns)')
    ax2.set_ylabel('Counts (Log Scale)')
    ax2.set_title('Typical PALS Spectrum in a Polymer')
    ax2.set_ylim(bottom=1)
    ax2.set_xlim(12.5, 25)
    ax2.legend()
    st.pyplot(fig2)
