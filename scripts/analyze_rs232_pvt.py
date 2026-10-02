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

noise_levels = np.linspace(0.01, 0.25, 25)
kl_unopt_curve = []
kl_masked_curve = []
snr_unopt_curve = []
snr_masked_curve = []

mean_activity = np.mean(clean) + 40.0
rms_u = np.sqrt(np.mean((unopt - clean) ** 2))
rms_m = np.sqrt(np.mean((masked - clean) ** 2))

for nl in noise_levels:
    # Environmental PVT baseline pedestal grows with process/temperature drift
    pedestal = mean_activity * (1.0 + 18.0 * nl)
    P = (clean + pedestal) / np.sum(clean + pedestal)
    Q_u = (unopt + pedestal) / np.sum(unopt + pedestal)
    Q_m = (masked + pedestal) / np.sum(masked + pedestal)

    kl_unopt_curve.append(entropy(P, Q_u))
    kl_masked_curve.append(entropy(P, Q_m))

    sigma = nl * mean_activity
    snr_unopt_curve.append(20 * np.log10(rms_u / sigma))
    snr_masked_curve.append(20 * np.log10(rms_m / sigma))

idx_10pct = 9
kl_u_10 = kl_unopt_curve[idx_10pct]
kl_m_10 = kl_masked_curve[idx_10pct]
masking_reduction = (1.0 - (kl_m_10 / kl_u_10)) * 100.0
gate_reduction = (1.0 - ((gates_masked - gates_clean) / (gates_unopt - gates_clean))) * 100.0

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

ax1.plot(noise_levels * 100, kl_unopt_curve, "o-", color="#e74c3c", label="Unoptimized RS232 Trojan")
ax1.plot(noise_levels * 100, kl_masked_curve, "s-", color="#2980b9", label="Synthesized-Masked RS232 Trojan")
ax1.axhline(y=0.0025, color="black", linestyle="--", label="SCA Detection Limit (0.0025 nats)")
ax1.axvspan(10, 20, color="gray", alpha=0.18, label="Typical Silicon PVT Variation (10-20%)")
ax1.set_xlabel("PVT Environmental Noise Variation (%)")
ax1.set_ylabel("Kullback-Leibler Divergence D_KL (nats)")
ax1.set_title("RS232 Benchmark: KL Divergence Attenuation Under PVT Noise")
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
print(f"Updated Phase 3 Plot (Masking Reduction: {masking_reduction:.2f}%)")
