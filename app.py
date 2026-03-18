import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

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
    
    # Simulate a random walk (thermalization path)
    st.subheader("Simulated Positron Path (Random Walk)")
    steps = st.slider("Number of collision steps", min_value=100, max_value=5000, value=1000, step=100)
    
    np.random.seed(42)
    # Generate random angles and uniform step sizes
    theta = np.random.uniform(0, 2*np.pi, steps)
    r = np.random.uniform(0, 1, steps) * np.exp(-np.linspace(0, 5, steps)) # Steps get shorter as energy drops
    
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
    Positron Annihilation Lifetime Spectroscopy (PALS) measures the time difference between the positron's emission and its annihilation. Because there are different decay pathways, the resulting statistical spectrum is a combination of several exponential decays.
    """)
    
    st.latex(r"N(t) = \sum_{i=1}^{k} \frac{I_i}{\tau_i} \exp\left(-\frac{t}{\tau_i}\right) + \text{Background}")
    
    st.markdown("""
    Where $I_i$ is the intensity (probability) and $\tau_i$ is the lifetime of the $i$-th component. 
    
    When building mathematical models to fit these spectra, navigating the parameter space can be difficult. In specialized optimization routines, rather than varying all individual parameters freely, it is often much more robust to optimize for only the ratio between specific component states (such as the ratio between the $M_0$ and $M_2$ components). 
    
    Furthermore, when correlating these lifetimes to physical polymer structures, you generally want to isolate variables. For example, keeping other matrix properties constant so that only the repulsion is changed allows researchers to cleanly observe how atomic repulsive forces directly dictate cavity size and o-Ps pick-off rates.
    """)
    
    # Generate Synthetic PALS Data
    st.subheader("Simulated Multi-Component Spectrum")
    
    t = np.linspace(0, 10, 1000) # Time in nanoseconds
    
    # Components (Lifetimes in ns, Intensities in relative %)
    tau1, I1 = 0.125, 20  # p-Ps
    tau2, I2 = 0.400, 50  # Free positron
    tau3, I3 = 2.000, 30  # o-Ps pick-off
    
    decay1 = (I1/tau1) * np.exp(-t/tau1)
    decay2 = (I2/tau2) * np.exp(-t/tau2)
    decay3 = (I3/tau3) * np.exp(-t/tau3)
    
    total_decay = decay1 + decay2 + decay3
    # Add some Poisson noise to simulate real statistics
    noisy_decay = total_decay + np.random.normal(0, max(total_decay)*0.02, len(t))
    noisy_decay = np.abs(noisy_decay) # Prevent negative values for log scale
    
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.plot(t, noisy_decay, '.', color='black', alpha=0.3, label='Raw Data (Counts)')
    ax2.plot(t, total_decay, 'r-', linewidth=2, label='Total Fit Model')
    ax2.plot(t, decay1, '--', label='Component 1: p-Ps (~125 ps)')
    ax2.plot(t, decay2, '--', label='Component 2: Free e+ (~400 ps)')
    ax2.plot(t, decay3, '--', label='Component 3: o-Ps Pick-off (~2 ns)')
    
    ax2.set_yscale('log')
    ax2.set_xlabel('Time (ns)')
    ax2.set_ylabel('Counts (Log Scale)')
    ax2.set_title('Typical PALS Spectrum in a Polymer')
    ax2.set_ylim(bottom=1)
    ax2.legend()
    st.pyplot(fig2)
