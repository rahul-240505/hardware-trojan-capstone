import numpy as np
from scipy.stats import entropy
from vcdvcd import VCDVCD

def extract_cycle_toggles(vcd_path, clock_period=10000, max_time=1520000):
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

clean = extract_cycle_toggles("vcd/gls_clean.vcd")
unopt = extract_cycle_toggles("vcd/gls_unopt.vcd")
masked = extract_cycle_toggles("vcd/gls_masked.vcd")

np.random.seed(42)
noise = lambda x: np.abs(x + np.random.normal(25.0, 5.0, len(x)))

P_clean = noise(clean)
P_clean /= np.sum(P_clean)

Q_unopt = noise(unopt)
Q_unopt /= np.sum(Q_unopt)

Q_masked = noise(masked)
Q_masked /= np.sum(Q_masked)

kl_unopt = entropy(P_clean, Q_unopt)
kl_masked = entropy(P_clean, Q_masked)
masking_pct = (1.0 - (kl_masked / kl_unopt)) * 100

print("\n================ GATE-LEVEL SYNTHESIS MASKING REPORT ================")
print(f"1. Clean Gate-Level Toggles:               {int(np.sum(clean))}")
print(f"2. Unoptimized Trojan Gate-Level Toggles:  {int(np.sum(unopt))}")
print(f"3. Synthesized-Masked Trojan Toggles:      {int(np.sum(masked))}")
print("---------------------------------------------------------------------")
print(f"KL Divergence (Unoptimized Trojan):        {kl_unopt:.6f} nats")
print(f"KL Divergence (After Synthesis-Masking):   {kl_masked:.6f} nats")
print(f"Synthesis-Masking Obscuration Ratio:       {masking_pct:.2f}% hidden!")
print("=====================================================================\n")
