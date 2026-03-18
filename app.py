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
    It ionizes atoms and excites electrons, losing kinetic energy at each step until it reaches thermal equilibrium (thermalization).
    """)
    
    st.subheader("Simulated Positron Path (Random Walk)")
    # Unique key for slider
    steps = st.slider("Number of collision steps", min_value=100, max_value=5000, value=1000, step=100, key="path_steps_slider")
    
    np.random.seed(42)
    theta_rand = np.random.uniform(0, 2*np.pi, steps)
    r_rand = np.random.uniform(0, 1, steps) * np.exp(-np.linspace(0, 5, steps)) 
    
    x_path = np.cumsum(r_rand * np.cos(theta_rand))
    y_path = np.cumsum(r_rand * np.sin(theta_rand))
    
    fig_path, ax_path = plt.subplots(figsize=(8, 5))
    ax_path.plot(x_path, y_path, alpha=0.6, color='blue', label='Positron Path')
    ax_path.scatter(x_path[0], y_path[0], color='green', s=100, label='Emission Point', zorder=5)
    ax_path.scatter(x_path[-1], y_path[-1], color='red', s=100, label='Thermalization Point', zorder=5)
    ax_path.set_title("Positron Thermalization in a Polymer Matrix")
    ax_path.axis('off')
    ax_path.legend()
    st.pyplot(fig_path)

# ==========================================
# TAB 2: Positronium Formation
# ==========================================
with tab2:
    st.header("Step-by-Step: Localization & Positronium Formation")

    st.markdown("""
    ### Step 1: Seeking the Void (Localization)
    As the positron reaches thermal equilibrium, it is naturally funneled away from the dense molecular backbone and pushed into the microscopic empty spaces—the **free volume cavities**.
    """)
    
    st.markdown("---")
    
    # --- Generate Energy Landscape & Paths ---
    np.random.seed(42)
    points_x, points_y = [], []
    chain_segments = []
    x_starts = np.linspace(0.5, 9.5, 14)
    
    for x_s in x_starts:
        curr_x, segment_x, segment_y = x_s, [x_s], [0.0]
        is_broken = (3.5 < x_s < 6.5)
        for y_s in np.linspace(0.2, 10.0, 45):
            if is_broken and (4.0 < y_s < 6.0):
                if len(segment_x) > 1: chain_segments.append((segment_x, segment_y))
                segment_x, segment_y, curr_x = [], [], x_s + np.random.normal(0, 0.3)
                continue
            curr_x += np.random.normal(0, 0.12)
            dist = np.sqrt((curr_x - 5.0)**2 + (y_s - 5.0)**2)
            if dist < 1.6:
                ang = np.arctan2(y_s - 5.0, curr_x - 5.0)
                curr_x = 5.0 + 1.6 * np.cos(ang)
            segment_x.append(curr_x); segment_y.append(y_s); points_x.append(curr_x); points_y.append(y_s)
        if len(segment_x) > 1: chain_segments.append((segment_x, segment_y))

    x_grid = np.linspace(0, 10, 100); y_grid = np.linspace(0, 10, 100)
    X, Y = np.meshgrid(x_grid, y_grid); Z = np.zeros_like(X)
    for px, py in zip(points_x, points_y):
        Z += 1.2 * np.exp(-((X - px)**2 + (Y - py)**2) / 0.25)
    Z = np.clip(Z + 0.5, 0, 15)
    min_idx = np.unravel_index(np.argmin(Z), Z.shape)
    cavity_x, cavity_y, cavity_z = X[min_idx], Y[min_idx], Z[min_idx]
    
    path_t = np.linspace(0, 1, 25)
    start_x, start_y = 5.0, 0.5
    path_x = start_x + (cavity_x - start_x) * path_t
    path_y = start_y + (cavity_y - start_y) * path_t
    path_z = scipy.ndimage.map_coordinates(Z, [path_y * 10, path_x * 10], order=1) + 0.3

    col1_tab2, col2_tab2 = st.columns(2)
    with col1_tab2:
        st.subheader("1. Amorphous Polymer Matrix")
        fig_struct, ax_struct = plt.subplots(figsize=(6, 6))
        for cx, cy in chain_segments:
            ax_struct.plot(cx, cy, '-', color='#4a69bd', alpha=0.7, linewidth=2.5)
        ax_struct.plot(path_x, path_y, 'w--', linewidth=2.5, label="Positron Path")
        ax_struct.scatter(cavity_x, cavity_y, color='#ff4757', s=250, marker='*', zorder=5, label="Void")
        ax_struct.set_facecolor('#1e272e'); ax_struct.legend()
        st.pyplot(fig_struct)

    with col2_tab2:
        st.subheader("2. Resulting Energy Landscape")
        fig_loc = go.Figure()
        fig_loc.add_trace(go.Surface(z=Z, x=x_grid, y=y_grid, colorscale='Plasma', opacity=0.9))
        fig_loc.add_trace(go.Scatter3d(x=path_x, y=path_y, z=path_z, mode='lines', line=dict(color='white', width=6)))
        fig_loc.update_layout(height=500, margin=dict(l=0, r=0, b=0, t=0), scene=dict(xaxis_visible=False, yaxis_visible=False))
        st.plotly_chart(fig_loc, use_container_width=True, key="energy_landscape_surface")

    # --- Step 2: The Spur Model ---
    st.divider()
    st.header("Step 2: Capturing a Partner & Forming Positronium")
    st.markdown(r"""
    As the positron ($e^+$) enters the polymer, it knocks electrons ($e^-$) off polymer molecules, creating a **Spur** of ionized centers. 
    The positron eventually captures one of these electrons to form Positronium (Ps).
    """)

    # Discrete Scattering Spur Viz
    np.random.seed(50)
    n_coll, start_p = 12, np.array([10, -8, 8])
    path_spur = np.zeros((n_coll, 3)); path_spur[0] = start_p
    for i in range(1, n_coll):
        pull = -path_spur[i-1] / np.linalg.norm(path_spur[i-1]) * 2.5
        path_spur[i] = path_spur[i-1] + np.random.normal(0, 1.8, 3) + pull
    
    ions_x, ions_y, ions_z = path_spur[:-1, 0], path_spur[:-1, 1], path_spur[:-1, 2]
    ele_x = ions_x + np.random.normal(0, 0.5, n_coll-1)
    ele_y = ions_y + np.random.normal(0, 0.5, n_coll-1)
    ele_z = ions_z + np.random.normal(0, 0.5, n_coll-1)

    fig_spur = go.Figure()
    fig_spur.add_trace(go.Scatter3d(x=path_spur[:,0], y=path_spur[:,1], z=path_spur[:,2], mode='lines', line=dict(color='white', width=4), name='e+ Path'))
    fig_spur.add_trace(go.Scatter3d(x=ions_x, y=ions_y, z=ions_z, mode='markers', marker=dict(color='#ffa502', size=6, symbol='x'), name='Ion (M+)'))
    fig_spur.add_trace(go.Scatter3d(x=ele_x, y=ele_y, z=ele_z, mode='markers', marker=dict(color='#1e90ff', size=4), name='e- Spur'))
    fig_spur.update_layout(height=600, scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_spur, use_container_width=True, key="spur_model_interactive")

    # --- Step 3 & 4: Spin States ---
    st.divider()
    st.header("Step 3 & 4: Quantum Spin States")
    
    col_a, col_b = st.columns(2)
    def create_mini_ps(is_ortho):
        theta = np.linspace(0, 2*np.pi, 100)
        fig = go.Figure()
        fig.add_trace(go.Scatter3d(x=np.cos(theta), y=np.sin(theta), z=np.zeros(100), mode='lines', line=dict(color='gray')))
        fig.add_trace(go.Scatter3d(x=[1], y=[0], z=[0], mode='markers', marker=dict(color='#ff4757', size=10)))
        z_c = 0.8 if is_ortho else -0.8
        fig.add_trace(go.Scatter3d(x=[-1], y=[0], z=[0], mode='markers', marker=dict(color='#4a69bd', size=10)))
        fig.add_trace(go.Cone(x=[-1], y=[0], z=[z_c], u=[0], v=[0], w=[0.5 if is_ortho else -0.5], showscale=False))
        fig.update_layout(height=300, margin=dict(l=0, r=0, b=0, t=0), scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False))
        return fig

    with col_a:
        st.subheader("Para-Positronium (p-Ps)")
        st.plotly_chart(create_mini_ps(False), use_container_width=True, key="para_orbit_viz")
        st.write("Singlet State (S=0) - 25% Probability")
    with col_b:
        st.subheader("Ortho-Positronium (o-Ps)")
        st.plotly_chart(create_mini_ps(True), use_container_width=True, key="ortho_orbit_viz")
        st.write("Triplet State (S=1) - 75% Probability")

    # --- Step 5: Hyperfine Splitting ---
    st.divider()
    st.header("Step 5: Hyperfine Splitting")
    fig_hfs, (ax_h1, ax_h2) = plt.subplots(1, 2, figsize=(12, 5))
    fig_hfs.patch.set_facecolor('#0e1117')
    ax_h1.set_facecolor('#0e1117'); ax_h1.axis('off')
    ax_h1.hlines(0, 1, 2, color='gray', linestyles='--')
    ax_h1.hlines(1.5, 3, 4, color='#ff4757', lw=4); ax_h1.text(4.1, 1.5, "o-Ps", color='white')
    ax_h1.hlines(-0.5, 3, 4, color='#4a69bd', lw=4); ax_h1.text(4.1, -0.5, "p-Ps", color='white')
    ax_h2.set_facecolor('#0e1117'); ax_h2.axis('off')
    ax_h2.text(0.5, 0.5, "Magnetic Interaction\nSplits Energy Levels", color='white', ha='center')
    st.pyplot(fig_hfs)

# ==========================================
# TAB 3: Decay Rules & Pick-Off
# ==========================================
with tab3:
    st.header("Charge Parity & The Forbidden Decay")
    st.markdown(r"Annihilation must conserve **Charge Parity ($C$-parity)**.")
    st.latex(r"C_{\text{Positronium}} = (-1)^{L+S}")
    
    st.markdown("""
    * **Para-Ps ($S=0$):** $C=+1$. Decays into **2 photons**.
    * **Ortho-Ps ($S=1$):** $C=-1$. Decays into **3 photons** (statistical bottleneck).
    """)
    
    st.divider()
    st.header("The Pick-Off Loophole")
    st.markdown("o-Ps 'picks off' an opposite-spin electron from the polymer wall to decay faster.")
    
    fig_dec, (ax_d1, ax_d2) = plt.subplots(1, 2, figsize=(14, 7))
    fig_dec.patch.set_facecolor('#0e1117')
    for ax in [ax_d1, ax_d2]:
        ax.set_facecolor('#1e272e'); ax.axis('off'); ax.set_xlim(-2, 2); ax.set_ylim(-2, 2)
    
    # 3-photon viz
    ax_d1.plot(0, 0, 'ro'); ax_d1.plot(0.3, 0, 'bo')
    for ang in [0, 2*np.pi/3, 4*np.pi/3]:
        ax_d1.plot([0, 1.5*np.cos(ang)], [0, 1.5*np.sin(ang)], color='gold', lw=2)
    
    # Pick-off viz
    ax_d2.add_patch(patches.Rectangle((0.8, -2), 1.2, 4, color='#485e74', alpha=0.6))
    ax_d2.plot(0.6, 0, 'ro'); ax_d2.plot(1.0, 0, 'bo')
    ax_d2.arrow(0.6, -0.2, 0, 0.4, color='red'); ax_d2.arrow(1.0, 0.2, 0, -0.4, color='blue')
    st.pyplot(fig_dec)
    st.info(r"The measured lifetime ($\tau_3$) is a proxy for hole size.")

# ==========================================
# TAB 4: PALS Statistics
# ==========================================
with tab4:
    st.header("PALS Statistics: Multi-Component Spectra")
    st.latex(r"N(t) = B + \sum A_i \exp(-(t-t_0)/\tau_i)")
    
    # Generate Spectrum
    x_spec = np.linspace(12, 25, 1000); t0_spec = 13.5; sig_spec = 0.12
    c1 = 25000 * np.exp(-(x_spec-t0_spec)/0.25) * erfc(1/np.sqrt(2) * (sig_spec/0.25 - (x_spec-t0_spec)/sig_spec))
    c3 = 350 * np.exp(-(x_spec-t0_spec)/1.68) * erfc(1/np.sqrt(2) * (sig_spec/1.68 - (x_spec-t0_spec)/sig_spec))
    
    fig_pals, ax_pals = plt.subplots(figsize=(10, 6))
    ax_pals.plot(x_spec, c1 + c3 + 2, 'r-', label="Total Fit")
    ax_pals.set_yscale('log'); ax_pals.set_ylim(1, 30000); ax_pals.legend()
    st.pyplot(fig_pals)
