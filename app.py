import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc

# --- App Configuration ---
st.set_page_config(page_title="Positron Annihilation Explorer", layout="wide")

st.title("Positron Annihilation in Polymers")
st.markdown("Explore the lifecycle of a positron, from its turbulent path through matter to the quantum rules of its decay, and the resulting PALS statistics.")

# --- Create Tabs for Step-by-Step Flow ---
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Path Through Matter", 
    "2. Positronium Formation", 
    "3. The Triplet State", 
    "4. PALS Statistics"
])

# ==========================================
# TAB 1: Path Through Matter
# ==========================================
with tab1:
    st.header("Thermalization: The Path Through Matter")
    st.markdown("""
    When a high-energy positron is emitted into a polymer like polyacrylic, it doesn't just stop immediately. It undergoes a series of rapid, inelastic collisions with the polymer chains. 
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
    st.header("Localization & Positronium Formation")
    st.markdown("""
    Once the positron slows down (red dot in the previous tab), it seeks out regions of low electron density due to the strong exchange repulsion from the dense electron clouds of the polymer chains. 
    It gets trapped in "free volume" cavities. Here, it can capture an electron to form **Positronium (Ps)**.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Para-positronium (p-Ps)** \n\n* Singlet state \n* Anti-parallel spins (S=0) \n* Intrinsic lifetime: ~125 ps \n* Decays into 2 gamma rays.")
    with col2:
        st.warning("**Ortho-positronium (o-Ps)** \n\n* Triplet state \n* Parallel spins (S=1) \n* Vacuum lifetime: ~142 ns \n* Trapped in polymer cavities.")

# ==========================================
# TAB 3: The Triplet State (Decay Rules)
# ==========================================
with tab3:
    st.header("Why Ortho-Positronium Cannot Decay Directly")
    st.markdown("""
    The triplet state (o-Ps) cannot decay directly into the standard 2 gamma-ray photons because of the strict conservation of **Charge Parity (C-parity)**.
    """)
    
    st.latex(r"C = (-1)^{L+S}")
    
    st.markdown("""
    * For o-Ps, the total spin $S = 1$, and orbital angular momentum $L = 0$.
    * Therefore, its C-parity is $(-1)^{0+1} = -1$.
    * A photon has a C-parity of $-1$. To conserve C-parity, o-Ps *must* decay into an **odd** number of photons.
    
    Because decaying into 1 photon violates momentum conservation, o-Ps is forced to decay into **3 photons**, which is an incredibly slow quantum process. 
    
    ### The Pick-Off Loophole
    In polyacrylics, the o-Ps doesn't survive long enough for the 3-photon decay. It bounces against the cavity walls and "picks off" an electron with an opposite spin from the polymer chain, allowing a fast 2-photon annihilation.
    """)

# ==========================================
# TAB 4: PALS Statistics
# ==========================================
with tab4:
    st.header("PALS Statistics: Multi-Component Spectra")
    st.markdown("""
    Positron Annihilation Lifetime Spectroscopy (PALS) measures the time difference between the positron's emission and its annihilation. Because there are different decay pathways, the resulting statistical spectrum is a combination of several exponential decays convolved with the detector's timing resolution (a Gaussian smearing effect).
    """)
    
    st.latex(r"N(t) = B + \sum_{i=1}^{k} A_i \exp\left(-\frac{t-t_0}{\tau_i}\right) \text{erfc}\left( \frac{1}{\sqrt{2}} \left( \frac{\sigma}{\tau_i} - \frac{t-t_0}{\sigma} \right) \right)")
    
    st.markdown("""
    When building mathematical models to fit these spectra, navigating the parameter space can be difficult. In specialized optimization routines, rather than varying all individual parameters freely, it is often much more robust to optimize for only the ratio between specific component states (such as the ratio between the M0 and M2 components). 
    
    Furthermore, when correlating these lifetimes to physical polymer structures, you generally want to isolate variables. For example, keeping other matrix properties constant so that only the repulsion is changed allows researchers to cleanly observe how atomic repulsive forces directly dictate cavity size and o-Ps pick-off rates.
    """)
    
    st.subheader("Simulated Multi-Component Spectrum (Realistic Instrument Resolution)")
    
    # Generate Realistic PALS Data
    x_data = np.linspace(12, 25, 1000) # Time in nanoseconds
    sigma = 0.297 / 2.35 # Typical detector resolution
    t0 = 13.5 # Time zero
    
    # Components (Amplitudes and Lifetimes in ns)
    A1, tau1 = 25000, 0.25  # p-Ps
    A2, tau2 = 1700, 0.61   # Free positron
    A3, tau3 = 350, 1.68    # o-Ps pick-off
    B = 2.0                 # Background noise
    
    # Calculate convoluted decays
    comp1 = A1 * np.exp(-(x_data-t0)/tau1) * erfc(1/np.sqrt(2) * (sigma/tau1 - (x_data-t0)/sigma))
    comp2 = A2 * np.exp(-(x_data-t0)/tau2) * erfc(1/np.sqrt(2) * (sigma/tau2 - (x_data-t0)/sigma))
    comp3 = A3 * np.exp(-(x_data-t0)/tau3) * erfc(1/np.sqrt(2) * (sigma/tau3 - (x_data-t0)/sigma))
    
    total_decay = comp1 + comp2 + comp3 + B
    
    # Add Poisson noise to simulate real statistics
    np.random.seed(42)
    noisy_decay = np.random.poisson(np.maximum(total_decay, 0))
    
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.plot(x_data, noisy_decay, '.', color='black', alpha=0.3, label='Raw Data (Counts)')
    ax2.plot(x_data, total_decay, 'r-', linewidth=2, label='Total Fit Model')
    ax2.plot(x_data, comp1, '--', label=f'Component 1: p-Ps (~{tau1*1000:.0f} ps)')
    ax2.plot(x_data, comp2, '--', label=f'Component 2: Free e+ (~{tau2*1000:.0f} ps)')
    ax2.plot(x_data, comp3, '--', label=f'Component 3: o-Ps (~{tau3:.2f} ns)')
    
    ax2.set_yscale('log')
    ax2.set_xlabel('Time (ns)')
    ax2.set_ylabel('Counts (Log Scale)')
    ax2.set_title('Typical PALS Spectrum in a Polymer')
    ax2.set_ylim(bottom=1)
    ax2.set_xlim(12.5, 25)
    ax2.legend()
    st.pyplot(fig2)
