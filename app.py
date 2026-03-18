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
    steps = st.slider("Number of collision steps", min_value=100, max_value=5000, value=1000, step=100, key="slider_tab1")
    
    np.random.seed(42)
    theta_p = np.random.uniform(0, 2*np.pi, steps)
    r_p = np.random.uniform(0, 1, steps) * np.exp(-np.linspace(0, 5, steps)) 
    x_p = np.cumsum(r_p * np.cos(theta_p))
    y_p = np.cumsum(r_p * np.sin(theta_p))
    
    fig_p, ax_p = plt.subplots(figsize=(8, 5))
    ax_p.plot(x_p, y_p, alpha=0.6, color='#1e90ff', label='Positron Path')
    ax_p.scatter(x_p[0], y_p[0], color='#2ed573', s=100, label='Emission', zorder=5)
    ax_p.scatter(x_p[-1], y_p[-1], color='#ff4757', s=100, label='Thermalization', zorder=5)
    ax_p.set_facecolor('#0e1117'); ax_p.axis('off'); ax_p.legend()
    st.pyplot(fig_p)

# ==========================================
# TAB 2: Positronium Formation
# ==========================================
with tab2:
    st.header("Localization & Positronium Formation")

    st.markdown("""
    ### Step 1: Seeking the Void (Localization)
    As the positron reaches thermal equilibrium, it is repelled by the dense atomic cores and pushed into the microscopic empty spaces—the **free volume cavities**.
    """)
    
    # --- Generate Energy Landscape ---
    np.random.seed(42)
    points_x, points_y, chain_segments = [], [], []
    x_starts = np.linspace(0.5, 9.5, 14)
    for xs in x_starts:
        cx, sx, sy = xs, [xs], [0.0]
        broken = (3.5 < xs < 6.5)
        for ys in np.linspace(0.2, 10.0, 45):
            if broken and (4.0 < ys < 6.0):
                if len(sx) > 1: chain_segments.append((sx, sy))
                sx, sy, cx = [], [], xs + np.random.normal(0, 0.3)
                continue
            cx += np.random.normal(0, 0.12)
            if np.sqrt((cx-5)**2 + (ys-5)**2) < 1.6:
                ang = np.arctan2(ys-5, cx-5); cx = 5 + 1.6*np.cos(ang)
            sx.append(cx); sy.append(ys); points_x.append(cx); points_y.append(ys)
        if len(sx) > 1: chain_segments.append((sx, sy))

    xg, yg = np.meshgrid(np.linspace(0,10,100), np.linspace(0,10,100))
    zg = np.zeros_like(xg)
    for px, py in zip(points_x, points_y): zg += 1.2 * np.exp(-((xg-px)**2 + (yg-py)**2) / 0.25)
    zg = np.clip(zg + 0.5, 0, 15)
    
    midx = np.unravel_index(np.argmin(zg), zg.shape)
    cvx, cvy, cvz = xg[midx], yg[midx], zg[midx]
    
    c_tab2_1, c_tab2_2 = st.columns(2)
    with c_tab2_1:
        fig_mat, ax_mat = plt.subplots(figsize=(6,6))
        for cx, cy in chain_segments: ax_mat.plot(cx, cy, color='#4a69bd', alpha=0.5)
        ax_mat.scatter(cvx, cvy, color='#ff4757', s=200, marker='*', label="Void")
        ax_mat.set_facecolor('#1e272e'); ax_mat.legend()
        st.pyplot(fig_mat)
    with c_tab2_2:
        fig_l = go.Figure(data=[go.Surface(z=zg, colorscale='Plasma', opacity=0.8)])
        fig_l.update_layout(height=450, margin=dict(l=0, r=0, b=0, t=0), scene_xaxis_visible=False)
        st.plotly_chart(fig_l, use_container_width=True, key="landscape_key")

    st.divider()
    st.header("Step 2: The Spur Model")
    st.markdown(r"The positron captures an electron ($e^-$) from the **Spur** (ionization track).")
    
    np.random.seed(50); n_c = 12; s_p = np.array([10, -8, 8]); path_s = np.zeros((n_c, 3)); path_s[0] = s_p
    for i in range(1, n_c): path_s[i] = path_s[i-1] + np.random.normal(0, 1.8, 3) + (-path_s[i-1]/np.linalg.norm(path_s[i-1])*2.5)
    
    ix, iy, iz = path_s[:-1, 0], path_s[:-1, 1], path_s[:-1, 2]
    ex, ey, ez = ix + np.random.normal(0, 0.5, n_c-1), iy + np.random.normal(0, 0.5, n_c-1), iz + np.random.normal(0, 0.5, n_c-1)

    fig_s = go.Figure()
    fig_s.add_trace(go.Scatter3d(x=path_s[:,0], y=path_s[:,1], z=path_s[:,2], mode='lines', line=dict(color='white', width=4), name='e<sup>+</sup> Path'))
    fig_s.add_trace(go.Scatter3d(x=ix, y=iy, z=iz, mode='markers', marker=dict(color='#ffa502', size=6, symbol='x'), name='Ion (M<sup>+</sup>)'))
    fig_s.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='markers', marker=dict(color='#1e90ff', size=5), name='e<sup>-</sup> Spur'))
    fig_s.update_layout(height=600, scene_visible=False, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_s, use_container_width=True, key="spur_key")

    st.divider()
    st.header("Step 3 & 4: Quantum States & Multiplicity")
    st.markdown(r"""
    The **3:1 ratio** is dictated by quantum multiplicity: $g = 2S + 1$.
    
    | State | Total Spin ($S$) | Multiplicity | Spin Alignment | Probability |
    | :--- | :---: | :---: | :---: | :---: |
    | **Para-Ps** | $0$ | $1$ | $\uparrow\downarrow$ | **25%** |
    | **Ortho-Ps** | $1$ | $3$ | $\uparrow\uparrow$ | **75%** |
    """)

    c_s1, c_s2 = st.columns(2)
    def draw_orbit(is_o):
        t = np.linspace(0, 2*np.pi, 100)
        f = go.Figure()
        f.add_trace(go.Scatter3d(x=np.cos(t), y=np.sin(t), z=np.zeros(100), mode='lines', line=dict(color='gray', dash='dash')))
        f.add_trace(go.Scatter3d(x=[1], y=[0], z=[0], mode='markers', marker=dict(color='#ff4757', size=12)))
        zc = 0.8 if is_o else -0.8
        f.add_trace(go.Scatter3d(x=[-1], y=[0], z=[0], mode='markers', marker=dict(color='#4a69bd', size=12)))
        f.add_trace(go.Cone(x=[-1], y=[0], z=[zc], u=[0], v=[0], w=[0.5 if is_o else -0.5], showscale=False))
        f.update_layout(height=300, margin=dict(l=0, r=0, b=0, t=0), scene_visible=False)
        return f
    with c_s1: st.plotly_chart(draw_orbit(False), key="p_key"); st.write("Para-Ps (Singlet)")
    with c_s2: st.plotly_chart(draw_orbit(True), key="o_key"); st.write("Ortho-Ps (Triplet)")

    st.divider()
    st.header("Step 5: Hyperfine Splitting")
    fig_h, (ah1, ah2) = plt.subplots(1, 2, figsize=(12, 5))
    fig_h.patch.set_facecolor('#0e1117'); ah1.set_facecolor('#0e1117'); ah1.axis('off')
    ah1.hlines(0, 1, 2, color='gray', linestyles='--')
    ah1.text(0.5, 0, "Bohr Level", color='gray', ha='right')
    ah1.hlines(1.5, 3, 4, color='#ff4757', lw=4); ah1.text(4.1, 1.5, "o-Ps (Repulsive)", color='white')
    ah1.hlines(-0.5, 3, 4, color='#4a69bd', lw=4); ah1.text(4.1, -0.5, "p-Ps (Attractive)", color='white')
    ah1.annotate('', xy=(3.5, 1.5), xytext=(3.5, -0.5), arrowprops=dict(arrowstyle='<->', color='orange'))
    ah2.set_facecolor('#0e1117'); ah2.axis('off'); ah2.text(0.5, 0.5, "Magnetic Interaction Splits\nthe n=1 Ground State", color='white', ha='center', fontsize=12)
    st.pyplot(fig_h)

# ==========================================
# TAB 3: Decay Rules & Pick-Off
# ==========================================
with tab3:
    st.header("Charge Parity & The Forbidden Decay")
    st.markdown(r"Conservation of **Charge Parity**: $C = (-1)^{L+S}$.")
    st.latex(r"C_{\text{o-Ps}} = (-1)^{0+1} = -1 \implies \text{Odd photons required.}")
    
    st.header("The Pick-Off Loophole")
    st.markdown("o-Ps 'picks off' an opposite-spin electron from the wall to decay in 2 photons.")
    
    fig_d, (ad1, ad2) = plt.subplots(1, 2, figsize=(14, 7))
    fig_d.patch.set_facecolor('#0e1117')
    for ax in [ad1, ad2]: ax.set_facecolor('#1e272e'); ax.axis('off'); ax.set_xlim(-2, 2); ax.set_ylim(-2, 2)
    # Vacuum 3-gamma
    ad1.set_title("3-Photon Decay (Slow)", color='white')
    for a in [0, 120, 240]: ad1.plot([0, 1.5*np.cos(np.radians(a))], [0, 1.5*np.sin(np.radians(a))], 'y-', lw=2)
    # Pick-off
    ad2.set_title("Pick-Off Decay (Fast)", color='white')
    ad2.add_patch(patches.Rectangle((0.8, -2), 1.2, 4, color='gray', alpha=0.3))
    ad2.plot(0.6, 0, 'ro'); ad2.plot(1.0, 0, 'bo')
    ad2.arrow(0.6, -0.2, 0, 0.4, color='red', lw=2); ad2.arrow(1.0, 0.2, 0, -0.4, color='blue', lw=2)
    st.pyplot(fig_d)
    st.info(r"Measured lifetime ($\tau_3$) is a direct proxy for hole size.")

# ==========================================
# TAB 4: PALS Statistics
# ==========================================
with tab4:
    st.header("PALS Statistics")
    st.latex(r"N(t) = B + \sum A_i \exp(-(t-t_0)/\tau_i)")
    
    xd = np.linspace(12, 25, 1000); sig = 0.12; t0 = 13.5
    def g_decay(a, tau): return a * np.exp(-(xd-t0)/tau) * erfc(1/np.sqrt(2) * (sig/tau - (xd-t0)/sig))
    
    c1, c2, c3 = g_decay(25000, 0.25), g_decay(1700, 0.61), g_decay(350, 1.68)
    tot = c1 + c2 + c3 + 2.0; noisy = np.random.poisson(np.maximum(tot, 0))
    
    fig_pals, ax_pals = plt.subplots(figsize=(10, 6))
    ax_pals.plot(xd, noisy, 'k.', alpha=0.2, label='Data')
    ax_pals.plot(xd, tot, 'r-', lw=2, label='Total Fit')
    ax_pals.plot(xd, c3, 'g--', label='o-Ps Component (Hole Size)')
    ax_pals.set_yscale('log'); ax_pals.set_ylim(1, 40000); ax_pals.legend()
    ax_pals.set_facecolor('#f0f2f6'); fig_pals.patch.set_facecolor('#f0f2f6')
    st.pyplot(fig_pals)
