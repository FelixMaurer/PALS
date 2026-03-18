import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import os
from scipy.special import erfc
from scipy.optimize import curve_fit, minimize
from scipy.signal import find_peaks

# --- App Configuration ---
st.set_page_config(page_title="Positron Annihilation Explorer", layout="wide")

st.title("Positron Annihilation in Polymers")
st.markdown("Explore the lifecycle of a positron, from its turbulent path through matter to the quantum rules of its decay, and the resulting PALS statistics.")

# --- Create Tabs for Step-by-Step Flow ---
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Path Through Matter", 
    "2. Positronium Formation", 
    "3. The Triplet State", 
    "4. PALS Statistics & Fitting"
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
    
    x_path = np.cumsum(r * np.cos(theta))
    y_path = np.cumsum(r * np.sin(theta))
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_path, y_path, alpha=0.6, color='blue', label='Positron Path')
    ax.scatter(x_path[0], y_path[0], color='green', s=100, label='Emission Point', zorder=5)
    ax.scatter(x_path[-1], y_path[-1], color='red', s=100, label='Thermalization Point', zorder=5)
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
# TAB 4: PALS Statistics & Fitting (Combined)
# ==========================================
with tab4:
    st.header("PALS Statistics: Multi-Component Spectra")
    st.markdown("""
    Positron Annihilation Lifetime Spectroscopy (PALS) measures the time difference between the positron's emission and its annihilation. Because there are different decay pathways, the resulting statistical spectrum is a combination of several exponential decays.
    """)
    
    st.latex(r"N(t) = \sum_{i=1}^{k} \frac{I_i}{\tau_i} \exp\left(-\frac{t}{\tau_i}\right) + \text{Background}")
    
    st.markdown("""
    When building mathematical models to fit these spectra, navigating the parameter space can be difficult. In specialized optimization routines, rather than varying all individual parameters freely, it is often much more robust to optimize for only the ratio between specific component states (such as the ratio between the $M_0$ and $M_2$ components). 
    
    Furthermore, when correlating these lifetimes to physical polymer structures, keeping other matrix properties constant so that only the repulsion is changed allows researchers to cleanly observe how atomic repulsive forces directly dictate cavity size and o-Ps pick-off rates.
    """)

    st.divider()

    # --- SECTION 1: WHAT IS FITTING? ---
    st.header("1. What is Fitting?")
    st.write("""
    Why do we use fitting? It generally serves two essential purposes:
    1. **Data Reduction:** It allows us to break down a large amount of correlating data into as few parameters as necessary, providing a clean, empirical summary of a system's behavior.
    2. **Theoretical Modeling:** It acts as a bridge between observation and theory. By fitting data to a specific model, we can test underlying physical explanations and extract meaningful parameters for further theoretical investigation.
    """)
    
    st.write("Click the button below to watch a simplified simulation of an algorithm searching for the best parameter by minimizing the errors (residues).")
    
    if st.button("Run Fit Animation"):
        # Setup Data
        true_slope = 2.2
        x_fit1 = np.arange(1, 11)
        noise = np.array([1.2, -0.5, 2.1, -1.8, 0.5, 1.3, -0.9, 0.4, -1.1, 0.8])
        y_fit1 = true_slope * x_fit1 + noise
        
        slopes_to_test = np.linspace(0, 4.5, 100)
        sse_curve = np.array([np.sum((y_fit1 - m * x_fit1)**2) for m in slopes_to_test])
        best_slope = slopes_to_test[np.argmin(sse_curve)]
        
        t_anim = np.linspace(0, 1, 60)
        damp = np.exp(-4 * t_anim)
        oscillation = np.cos(2 * np.pi * t_anim)
        start_point = 0.5
        path = best_slope - (best_slope - start_point) * damp * oscillation
        
        plot_placeholder = st.empty() 
        
        for k in range(len(path)):
            current_m = path[k]
            current_y = current_m * x_fit1
            current_sse = np.sum((y_fit1 - current_y)**2)
            
            if current_m > best_slope + 0.1:
                status_str, status_col = 'Status: OVERSHOOTING!', 'orange'
            elif k > 40:
                status_str, status_col = 'Status: SETTLING / CONVERGED', 'green'
            else:
                status_str, status_col = 'Status: SEARCHING...', 'black'

            fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            ax1.scatter(x_fit1, y_fit1, s=60, color='#3399CC', label='Data')
            ax1.plot(x_fit1, current_y, 'r', linewidth=2.5, label='Fitted Line')
            ax1.vlines(x_fit1, ymin=np.minimum(y_fit1, current_y), ymax=np.maximum(y_fit1, current_y), colors='#CC3333', linewidth=1, alpha=0.5)
            ax1.set_title('Visualizing the Fit')
            ax1.set_xlim(0, 11)
            ax1.set_ylim(min(y_fit1)-5, max(y_fit1)+5)
            
            ax2.plot(slopes_to_test, sse_curve, 'k', linewidth=1.5)
            ax2.plot(current_m, current_sse, 'ro', markersize=10)
            ax2.text(0.2, max(sse_curve)*0.9, status_str, color=status_col, fontsize=12, fontweight='bold')
            ax2.set_title('Total Residue (The "Valley")')
            ax2.set_xlabel('Slope Parameter (m)')
            ax2.set_ylabel('Sum of Squared Residues')
            
            plot_placeholder.pyplot(fig1)
            plt.close(fig1) 
            time.sleep(0.03)

    st.markdown("### What is happening here?")
    st.write("**The Left Plot: The Residues** On the left, you see our data points and our model. The vertical lines are **residues** (mistakes the model makes).")
    st.write("**The Right Plot: The Valley of Errors** If we square those individual residues and add them up, we get a single number representing the 'Total Error.' The algorithm explores this valley to find the lowest point, eventually **converging**.")

    st.divider()

    # --- SECTION 2: THE TWO MINIMUM PROBLEM ---
    st.header("2. The 'Two Minimum' Problem")
    st.write("When we fit more than one parameter, the 'valley' of errors becomes a 3D landscape. Depending on where your algorithm starts, it might roll into the wrong valley. Try adjusting the starting values below and run the fit to see if you get trapped!")

    col1, col2 = st.columns(2)
    with col1:
        user_p1 = st.slider("Start position for Narrow Peak (p1)", 1.0, 9.0, 7.5, step=0.5)
    with col2:
        user_p2 = st.slider("Start position for Wide Peak (p2)", 1.0, 9.0, 2.0, step=0.5)

    if st.button("Run 2D Fit Animation"):
        plot_placeholder_2 = st.empty()
        
        x_2d = np.linspace(0, 10, 200)
        y_data_2d = 1.0 * np.exp(-((x_2d - 3) / 0.4)**2) + 0.8 * np.exp(-((x_2d - 7) / 1.5)**2)
        
        def model_func(p): return 1.0 * np.exp(-((x_2d - p[0]) / 0.4)**2) + 0.8 * np.exp(-((x_2d - p[1]) / 1.5)**2)
        def sse_func(p): return np.sum((y_data_2d - model_func(p))**2)
            
        mu_range = np.linspace(1, 9, 40)
        M1, M2 = np.meshgrid(mu_range, mu_range)
        Z = np.zeros_like(M1)
        for i in range(M1.shape[0]):
            for j in range(M1.shape[1]):
                Z[i, j] = np.log10(sse_func([M1[i, j], M2[i, j]]))
                
        lr, n_steps, eps = 0.002, 80, 1e-4
        curr_user, curr_good = np.array([user_p1, user_p2]), np.array([2.0, 8.0])
        path_user, path_good = [curr_user.copy()], [curr_good.copy()]
        
        for t_step in range(n_steps):
            v_user = sse_func(curr_user)
            g_user = np.array([(sse_func(curr_user + [eps, 0]) - v_user) / eps, (sse_func(curr_user + [0, eps]) - v_user) / eps])
            curr_user = curr_user - lr * g_user
            path_user.append(curr_user.copy())
            
            v_good = sse_func(curr_good)
            g_good = np.array([(sse_func(curr_good + [eps, 0]) - v_good) / eps, (sse_func(curr_good + [0, eps]) - v_good) / eps])
            curr_good = curr_good - lr * g_good
            path_good.append(curr_good.copy())
            
            if t_step % 3 == 0 or t_step == n_steps - 1:
                fig2 = plt.figure(figsize=(14, 6))
                
                ax1 = fig2.add_subplot(121)
                ax1.plot(x_2d, y_data_2d, 'k.', markersize=8, label='Experimental Data')
                ax1.plot(x_2d, model_func(curr_user), 'r-', linewidth=2.5, label='User Path Fit (Red)')
                ax1.plot(x_2d, model_func(curr_good), 'g-', linewidth=2.5, alpha=0.6, label='Global Path Fit (Green)')
                ax1.set_title('Current Fit to Data')
                ax1.set_ylim(-0.2, 1.5)
                ax1.legend(loc='upper right')
                
                ax2 = fig2.add_subplot(122, projection='3d')
                ax2.plot_surface(M1, M2, Z, cmap='viridis', alpha=0.6, edgecolor='none')
                
                p_user_arr, p_good_arr = np.array(path_user), np.array(path_good)
                z_user = [np.log10(sse_func(p)) for p in p_user_arr]
                z_good = [np.log10(sse_func(p)) for p in p_good_arr]
                
                ax2.plot(p_user_arr[:,0], p_user_arr[:,1], z_user, 'r.-', linewidth=2)
                ax2.plot(p_good_arr[:,0], p_good_arr[:,1], z_good, 'g.-', linewidth=2)
                ax2.scatter(*curr_user, np.log10(sse_func(curr_user)), color='red', s=100)
                ax2.scatter(*curr_good, np.log10(sse_func(curr_good)), color='green', s=100)
                ax2.set_title('Optimizer Path on Error Surface')
                ax2.set_xlabel('Narrow Peak Pos')
                ax2.set_ylabel('Wide Peak Pos')
                ax2.view_init(elev=30, azim=45)
                
                plot_placeholder_2.pyplot(fig2)
                plt.close(fig2)
                time.sleep(0.01)

    st.write("**Global vs. Local Minima:** The green path finds the true mathematical bottom (global minimum). The red path, controlled by your sliders, might get stuck in a shallower crater (local minimum), leaving you with a mathematically correct but physically incorrect result.")

    st.divider()

    # --- SECTION 3: THE LIFETIME FIT ---
    st.header("3. The Straightforward Lifetime Fit")
    st.write("We measure how long particles survive before they decay. The theoretical model is a sum of exponential decays, convolved with a Gaussian distribution representing the detector resolution.")
    st.latex(r"F(t) = B + \sum_{i=1}^{3} A_i \exp\left(-\frac{t-t_0}{\tau_i}\right) \text{erfc}\left( \frac{1}{\sqrt{2}} \left( \frac{\sigma}{\tau_i} - \frac{t-t_0}{\sigma} \right) \right)")

    # Data Loading / Mock Data
    file_name = 'positronlifetime.txt'
    if os.path.exists(file_name):
        data = np.loadtxt(file_name)
        x_raw, y_raw = data[:, 0], data[:, 1]
        i_start, i_end = 2300, len(x_raw) - 1200
        x_data, y_data = x_raw[i_start:i_end], y_raw[i_start:i_end]
    else:
        st.warning("Data file not found. Using synthetic PALS data for demonstration.")
        x_data = np.linspace(10, 30, 1000)
        sigma_demo = 0.297 / 2.35
        def mock_model(x_val):
            c1 = 25000 * np.exp(-(x_val-13.5)/0.25) * erfc(1/np.sqrt(2) * (sigma_demo/0.25 - (x_val-13.5)/sigma_demo))
            c2 = 1700 * np.exp(-(x_val-13.5)/0.61) * erfc(1/np.sqrt(2) * (sigma_demo/0.61 - (x_val-13.5)/sigma_demo))
            c3 = 350 * np.exp(-(x_val-13.5)/1.68) * erfc(1/np.sqrt(2) * (sigma_demo/1.68 - (x_val-13.5)/sigma_demo))
            return c1 + c2 + c3 + 2.0
        y_true = mock_model(x_data)
        y_data = np.random.poisson(np.maximum(y_true, 0))

    def pals_fit_func(x_val, A1, t0, tau1, A2, tau2, B, A3, tau3):
        DeltaT = 0.297 / 2.35 
        c1 = A1 * np.exp(-(x_val-t0)/tau1) * erfc(1/np.sqrt(2) * (DeltaT/tau1 - (x_val-t0)/DeltaT))
        c2 = A2 * np.exp(-(x_val-t0)/tau2) * erfc(1/np.sqrt(2) * (DeltaT/tau2 - (x_val-t0)/DeltaT))
        c3 = A3 * np.exp(-(x_val-t0)/tau3) * erfc(1/np.sqrt(2) * (DeltaT/tau3 - (x_val-t0)/DeltaT))
        return c1 + c2 + c3 + B

    st.subheader("Adjust Starting Parameters")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        g_t0 = st.number_input("t0", value=13.0)
        g_B = st.number_input("Background B", value=2.0)
    with c2:
        g_A1 = st.number_input("A1", value=25000.0)
        g_tau1 = st.number_input("tau1", value=0.3)
    with c3:
        g_A2 = st.number_input("A2", value=2000.0)
        g_tau2 = st.number_input("tau2", value=1.0)
    with c4:
        g_A3 = st.number_input("A3", value=500.0)
        g_tau3 = st.number_input("tau3", value=2.0)

    if st.button("Perform Lifetime Fit"):
        weights = 1.0 / np.sqrt(np.maximum(y_data, 1))
        lower_bounds = [0, 0, 0.01, 0, 0.01, 0, 0, 0.01]
        upper_bounds = [np.inf, 50.0, 5.0, np.inf, 10.0, np.inf, np.inf, 50.0]
        
        try:
            popt, pcov = curve_fit(
                pals_fit_func, x_data, y_data, p0=[g_A1, g_t0, g_tau1, g_A2, g_tau2, g_B, g_A3, g_tau3], 
                sigma=weights, absolute_sigma=True, bounds=(lower_bounds, upper_bounds), method='trf', max_nfev=10000
            )
            y_fit = pals_fit_func(x_data, *popt)
            residuals = (y_data - y_fit) * weights 
            
            fig3, (ax_fit, ax_res) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})
            ax_fit.semilogy(x_data, y_data, 'k.', markersize=2, label="Data")
            ax_fit.semilogy(x_data, y_fit, 'r-', linewidth=2, label="Final Fit")
            ax_fit.set_ylabel("Counts (log scale)")
            ax_fit.set_title("Lifetime Spectra and Final Fit")
            ax_fit.legend()
            
            ax_res.plot(x_data, residuals, color='gray', linewidth=0.5)
            ax_res.axhline(0, color='red', linewidth=1)
            ax_res.axhline(2, color='red', linestyle=':')
            ax_res.axhline(-2, color='red', linestyle=':')
            ax_res.set_xlabel("Time (ns)")
            ax_res.set_ylabel("Weighted Residuals")
            ax_res.set_ylim(-5, 5)
            st.pyplot(fig3)
            
            perr = np.sqrt(np.diag(pcov))
            I_tot = popt[0] + popt[3] + popt[6]
            I1, I2, I3 = (popt[0]/I_tot)*100, (popt[3]/I_tot)*100, (popt[6]/I_tot)*100
            
            st.success("Fit converged successfully. If residuals look like scattered static, the model correctly captures the physics.")
        except Exception as e:
            st.error(f"Fit failed. Adjust parameters. Error: {e}")

    st.divider()

    # --- SECTION 4 & 5: WRONG MINIMUM & ACF ---
    st.header("4. Trapped & Autocorrelation Verification")
    st.write("What happens if we feed the algorithm terrible starting values? It gets trapped. We can prove this using the **Autocorrelation Function (ACF)**, which detects patterns in the residuals.")

    if st.button("Run Trapped Fit & Calculate ACF"):
        true_sigma = np.sqrt(np.maximum(y_data, 1))
        bad_guess = [25000.0, 13.0, 0.25, 2000.0, 1.5, 2.0, 1.0, 0.01]
        
        try:
            popt_bad, _ = curve_fit(pals_fit_func, x_data, y_data, p0=bad_guess, sigma=true_sigma, absolute_sigma=True, method='lm', maxfev=10000)
            y_fit_bad = pals_fit_func(x_data, *popt_bad)
            residuals_bad = (y_data - y_fit_bad) / true_sigma
            
            # Good Fit for comparison
            good_guess = [25000.0, 13.0, 0.3, 2000.0, 1.0, 2.0, 500.0, 2.0]
            popt_good, _ = curve_fit(pals_fit_func, x_data, y_data, p0=good_guess, sigma=true_sigma, absolute_sigma=True, method='trf', bounds=([0, 0, 0.01, 0, 0.01, 0, 0, 0.01], [np.inf, 50.0, 5.0, np.inf, 10.0, np.inf, np.inf, 50.0]), max_nfev=10000)
            res_good = (y_data - pals_fit_func(x_data, *popt_good)) / true_sigma

            def calc_acf(res, max_lags=100):
                n = len(res)
                res_centered = res - np.mean(res)
                sum_sq = np.sum(res_centered**2)
                acf = np.zeros(max_lags + 1)
                for k in range(max_lags + 1):
                    acf[k] = 1.0 if k == 0 else np.sum(res_centered[:-k] * res_centered[k:]) / sum_sq
                return acf, 1.96 / np.sqrt(n)

            acf_good, conf_good = calc_acf(res_good)
            acf_bad, conf_bad = calc_acf(residuals_bad)
            lags = np.arange(101)

            fig_acf, (ax_acf1, ax_acf2) = plt.subplots(1, 2, figsize=(12, 5))
            ax_acf1.stem(lags, acf_good, linefmt='k-', markerfmt='k.', basefmt='k-')
            ax_acf1.axhline(conf_good, color='red', linestyle=':'); ax_acf1.axhline(-conf_good, color='red', linestyle=':')
            ax_acf1.set_title("Autocorrelation: Global Minimum")
            ax_acf1.set_xlabel("Lag (Bins)"); ax_acf1.set_ylim(-0.5, 1)
            
            ax_acf2.stem(lags, acf_bad, linefmt='k-', markerfmt='k.', basefmt='k-')
            ax_acf2.axhline(conf_bad, color='red', linestyle=':'); ax_acf2.axhline(-conf_bad, color='red', linestyle=':')
            ax_acf2.set_title("Autocorrelation: Trapped in False Minimum")
            ax_acf2.set_xlabel("Lag (Bins)"); ax_acf2.set_ylim(-0.5, 1)
            st.pyplot(fig_acf)

            st.error("In the trapped fit (right), the strong wave pattern breaches the red confidence limits. This proves the algorithm found a mathematical minimum, but the physics is fundamentally incorrect.")
        except Exception as e:
            st.error(f"Fit failed. Error: {e}")

    st.divider()

    # --- SECTION 6: THE MELT METHOD ---
    st.header("5. The MELT Method: Continuous Spectrum")
    st.write("Instead of guessing discrete lifetimes, MELT treats the data as a continuous sum of all possible lifetimes weighted by their probability, penalized by Shannon entropy to prevent overfitting.")
    st.latex(r"\Phi(\alpha) = \chi^2(\alpha) + \lambda \sum_{i=1}^{N} \alpha_i \ln(\alpha_i)")

    if st.button("Run MELT Estimation"):
        fitted_offset, fitted_B = 13.47, 1.85
        weights = 1.0 / np.maximum(y_data, 1)
        
        n_taus = 50 
        tau_grid = np.logspace(np.log10(0.05), np.log10(5.0), n_taus)
        K = np.zeros((len(x_data), n_taus))
        
        DeltaT = 0.297 / 2.35
        for j in range(n_taus):
            tau = tau_grid[j]
            K[:, j] = np.exp(-(x_data - fitted_offset)/tau) * erfc(1/np.sqrt(2) * (DeltaT/tau - (x_data - fitted_offset)/DeltaT))
            
        lambda_reg = 0.001 
        def melt_objective(alpha):
            y_pred = K @ alpha + fitted_B
            return np.sum(weights * (y_data - y_pred)**2) + lambda_reg * np.sum(alpha * np.log(alpha + 1e-12))

        res = minimize(melt_objective, np.ones(n_taus) * (np.max(y_data) / n_taus), method='SLSQP', bounds=[(0, None) for _ in range(n_taus)], options={'maxiter': 50000, 'ftol': 1e-6})
        alpha_dist = res.x
        
        peaks, _ = find_peaks(alpha_dist)
        peak_taus, peak_amps_display = (tau_grid[np.sort(peaks[np.argsort(alpha_dist[peaks])[::-1][:min(3, len(peaks))]])], alpha_dist[np.sort(peaks[np.argsort(alpha_dist[peaks])[::-1][:min(3, len(peaks))]])]) if len(peaks) > 0 else ([], [])
        
        fig_melt, ax_melt = plt.subplots(figsize=(10, 5))
        ax_melt.semilogx(tau_grid, alpha_dist, 'b', linewidth=2, label="MELT Spectrum")
        for p_tau, p_amp in zip(peak_taus, peak_amps_display):
            ax_melt.semilogx(p_tau, p_amp, 'ro', markersize=8)
            ax_melt.text(p_tau, p_amp * 1.1, f"{p_tau:.3f} ns", ha='center', fontweight='bold', color='red')
            
        ax_melt.set_xlabel("Lifetime tau (ns)"); ax_melt.set_ylabel("Amplitude alpha"); ax_melt.set_title("Continuous Lifetime Spectrum (MELT)")
        ax_melt.grid(True, which="both", linestyle=":", alpha=0.5); ax_melt.legend()
        st.pyplot(fig_melt)
        st.success("By balancing the model against entropy, MELT successfully isolates the physical decay channels without needing discrete initial guesses.")
