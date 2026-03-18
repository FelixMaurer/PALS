import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc
import matplotlib.patches as patches

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
    As the positron loses its kinetic energy and reaches thermal equilibrium, it must figure out where to "settle" within the polyacrylic matrix. It does not just stop randomly; its final location is strictly dictated by the microscopic forces of the polymer.

    **The Repulsive Landscape:** A polymer is a tangled mess of long molecular chains. These chains consist of dense, positively charged atomic nuclei (Carbon, Oxygen, Hydrogen) surrounded by tightly bound electron clouds. 
    
    Even though the positron is positively charged and theoretically attracted to electrons, it experiences massive **Coulomb repulsion** from the positive atomic cores of the polymer. Furthermore, once it begins to capture an electron to form Positronium, the newly formed atom experiences strong **exchange repulsion** (due to the Pauli exclusion principle) from the bulk electrons of the polymer chains.

    **The Free Volume Cavity:**
    Because of this intense repulsion, the polymer chains act like towering "hills" of high potential energy. Seeking the lowest possible energy state, the positron is naturally funneled away from the molecular backbone and pushed into the microscopic empty spaces—the **free volume cavities**—created by the irregular, twisted packing of the polyacrylic chains. 
    """)
    
    # --- Visualization of Localization Landscape ---
    st.subheader("Visualizing the Potential Energy Landscape")
    
    fig_loc, ax_loc = plt.subplots(figsize=(10, 6))
    
    # Generate a synthetic potential energy landscape
    np.random.seed(45)
    x_grid = np.linspace(0, 10, 100)
    y_grid = np.linspace(0, 10, 100)
    X, Y = np.meshgrid(x_grid, y_grid)
    
    # Create polymer chains as regions of high potential energy (sum of Gaussians)
    Z = np.zeros_like(X)
    num_atoms = 30
    for _ in range(num_atoms):
        x_c = np.random.uniform(-1, 11)
        y_c = np.random.uniform(-1, 11)
        # Gaussian representing atomic repulsion
        Z += 3.0 * np.exp(-((X - x_c)**2 + (Y - y_c)**2) / 1.5)
    
    # Plot the contour
    contour = ax_loc.contourf(X, Y, Z, levels=20, cmap='YlGnBu_r', alpha=0.8)
    cbar = fig_loc.colorbar(contour, ax=ax_loc)
    cbar.set_label('Potential Energy / Repulsive Force', rotation=270, labelpad=15)
    
    # Annotate the landscape
    ax_loc.text(1, 9, "High Energy\n(Polymer Chains)", color='white', fontweight='bold', fontsize=10)
    
    # Find the deepest cavity (minimum potential) to trap the positron
    min_idx = np.unravel_index(np.argmin(Z, axis=None), Z.shape)
    cavity_x = x_grid[min_idx[1]]
    cavity_y = y_grid[min_idx[0]]
    
    # Draw the localization path
    # Positron starts at a random high-energy edge and rolls into the cavity
    start_x, start_y = 8.0, 8.0
    path_x = [start_x, 7.5, 6.0, 5.0, 4.5, cavity_x]
    path_y = [start_y, 6.5, 5.0, 3.5, 2.5, cavity_y]
    
    ax_loc.plot(path_x, path_y, 'w--', linewidth=2, label="Positron Localization Path")
    ax_loc.plot(start_x, start_y, 'go', markersize=8, label="Thermalized Positron")
    ax_loc.plot(cavity_x, cavity_y, 'r*', markersize=15, label="Trapped inside Free Volume Void")
    
    # Add an outline to the cavity
    circle = plt.Circle((cavity_x, cavity_y), 1.2, color='red', fill=False, linestyle=':', linewidth=2)
    ax_loc.add_patch(circle)
    ax_loc.text(cavity_x, cavity_y + 1.5, "Deepest Void", color='red', ha='center', fontweight='bold')
    
    ax_loc.set_title("Positron Funneled into a Polymer Free Volume Cavity")
    ax_loc.set_xlabel("Nanometers (nm)")
    ax_loc.set_ylabel("Nanometers (nm)")
    ax_loc.legend(loc="upper right", facecolor='lightgray', framealpha=0.9)
    
    st.pyplot(fig_loc)

    st.markdown("""
    As seen in the contour plot above, the positron avoids the dark blue areas (the dense polyacrylic chains) and settles into the bright yellow areas (the physical voids). Once localized in the bottom of this potential energy "well", it is ready for Step 2: forming Positronium.
    """)

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
