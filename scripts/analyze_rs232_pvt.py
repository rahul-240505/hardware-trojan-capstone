import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy
from vcdvcd import VCDVCD

def count_gates(netlist_path):
    with open(netlist_path, "r") as f:
        text = f.read()
    return len(re.findall(r"_X1\s+\_\d+\_", text))

def extract_cycle_toggles(vcd_path, clock_period=10000, max_time=2020000):
    vcd = VCDVCD(vcd_path)
    num_bins = max_time // clock_period
    toggle_counts = np.zeros(num_bins)
    for signal_name in vcd.references_to_ids.keys():
        sig = vcd[signal_name]
        for timestamp, _ in sig.tv:
            if 0 < timestamp < max_time:
                bin_idx = timestamp // clock_period
                toggle_counts[bin_idx] += 1
    return toggle_counts

gates_clean = count_gates("netlist/rs232_clean_synth.v")
gates_unopt = count_gates("netlist/rs232_unopt_synth.v")
gates_masked = count_gates("netlist/rs232_masked_synth.v")

clean = extract_cycle_toggles("vcd/rs232_clean.vcd")
unopt = extract_cycle_toggles("vcd/rs232_unopt.vcd")
masked = extract_cycle_toggles("vcd/rs232_masked.vcd")

# Compute KL Divergence across PVT Noise Levels (1% to 25% environmental variance)
noise_levels = np.linspace(0.01, 0.25, 25)
kl_unopt_curve = []
kl_masked_curve = []
snr_unopt_curve = []
snr_masked_curve = []

mean_activity = np.mean(clean) + 40.0
np.random.seed(42)

for nl in noise_levels:
    sigma = nl * mean_activity
    n_clean = np.abs(clean + np.random.normal(mean_activity, sigma, len(clean)))
    n_unopt = np.abs(unopt + np.random.normal(mean_activity, sigma, len(unopt)))
    n_masked = np.abs(masked + np.random.normal(mean_activity, sigma, len(masked)))

    P = n_clean / np.sum(n_clean)
    Q_u = n_unopt / np.sum(n_unopt)
    Q_m = n_masked / np.sum(n_masked)

    kl_unopt_curve.append(entropy(P, Q_u))
    kl_masked_curve.append(entropy(P, Q_m))

    # Signal-to-Noise Ratio (dB) = 20 * log10(Trojan_Delta_RMS / PVT_Noise_Sigma)
    rms_u = np.sqrt(np.mean((unopt - clean) ** 2))
    rms_m = np.sqrt(np.mean((masked - clean) ** 2))
    snr_unopt_curve.append(20 * np.log10(rms_u / sigma))
    snr_masked_curve.append(20 * np.log10(rms_m / sigma))

idx_10pct = 9  # 10% PVT noise index
kl_u_10 = kl_unopt_curve[idx_10pct]
kl_m_10 = kl_masked_curve[idx_10pct]
masking_reduction = (1.0 - (kl_m_10 / kl_u_10)) * 100.0
gate_reduction = (1.0 - ((gates_masked - gates_clean) / (gates_unopt - gates_clean))) * 100.0

print("\n================ RS232 BENCHMARK: SYNTHESIS-MASKING & PVT REPORT ================")
print(f"Physical 45nm Gates (Clean Baseline):      {gates_clean} gates")
print(f"Physical 45nm Gates (Unoptimized Trojan):  {gates_unopt} gates (+{gates_unopt - gates_clean} Trojan gates)")
print(f"Physical 45nm Gates (Synthesized-Masked):  {gates_masked} gates (+{gates_masked - gates_clean} Trojan gates)")
print(f"Trojan Hardware Area Absorbed by Yosys:    {gate_reduction:.2f}%")
print("---------------------------------------------------------------------------------")
print(f"Total Gate Toggles (Clean RS232):          {int(np.sum(clean))}")
print(f"Total Gate Toggles (Unoptimized Trojan):   {int(np.sum(unopt))}")
print(f"Total Gate Toggles (Synthesized-Masked):   {int(np.sum(masked))}")
print("---------------------------------------------------------------------------------")
print(f"KL Divergence @ 10% PVT Noise (Unopt):     {kl_u_10:.6f} nats")
print(f"KL Divergence @ 10% PVT Noise (Masked):    {kl_m_10:.6f} nats")
print(f"Statistical KL-Divergence Masking Ratio:   {masking_reduction:.2f}% hidden by EDA synthesis!")
print(f"Side-Channel SNR @ 15% PVT (Masked):       {snr_masked_curve[14]:.2f} dB")
print("=================================================================================\n")

# Plot 2-Panel Phase 3 Dashboard
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

ax1.plot(noise_levels * 100, kl_unopt_curve, "o-", color="#e74c3c", label="Unoptimized RS232 Trojan")
ax1.plot(noise_levels * 100, kl_masked_curve, "s-", color="#2980b9", label="Synthesized-Masked RS232 Trojan")
ax1.axhline(y=0.015, color="black", linestyle="--", label="SCA Detection Threshold (0.015 nats)")
ax1.axvspan(10, 20, color="gray", alpha=0.18, label="Typical Silicon PVT Variation (10-20%)")
ax1.set_xlabel("PVT Environmental Noise Variation (%)")
ax1.set_ylabel("Kullback-Leibler Divergence D_KL (nats)")
ax1.set_title("RS232 Benchmark: KL Divergence vs. PVT Noise Barrier")
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(noise_levels * 100, snr_unopt_curve, "o-", color="#e74c3c", label="Unoptimized Trojan SNR (dB)")
ax2.plot(noise_levels * 100, snr_masked_curve, "s-", color="#2980b9", label="Synthesized-Masked Trojan SNR (dB)")
ax2.axhline(y=0.0, color="black", linestyle="--", label="0 dB Noise Floor (Signal < Noise)")
ax2.axvspan(10, 20, color="gray", alpha=0.18, label="Typical Silicon PVT Zone")
ax2.set_xlabel("PVT Environmental Noise Variation (%)")
ax2.set_ylabel("Side-Channel Signal-to-Noise Ratio (dB)")
ax2.set_title("Synthesis-Masking Pushes Trojan Below the PVT Noise Floor")
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("results_phase3_rs232.png", dpi=200)
print("Saved visual PVT & KL-Divergence report to: results_phase3_rs232.png")
