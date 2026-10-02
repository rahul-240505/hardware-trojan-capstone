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

clean_toggles = extract_cycle_toggles("vcd/clean.vcd")
trojan_toggles = extract_cycle_toggles("vcd/trojan.vcd")

np.random.seed(42)
pvt_noise_clean = np.abs(clean_toggles + np.random.normal(5.0, 1.5, len(clean_toggles)))
pvt_noise_trojan = np.abs(trojan_toggles + np.random.normal(5.0, 1.5, len(trojan_toggles)))

P = pvt_noise_clean / np.sum(pvt_noise_clean)
Q = pvt_noise_trojan / np.sum(pvt_noise_trojan)

kl_div = entropy(P, Q)
print("\n=== PRE-SYNTHESIS SWITCHING & KL DIVERGENCE ===")
print(f"Total Clean Toggles:   {int(np.sum(clean_toggles))}")
print(f"Total Trojan Toggles:  {int(np.sum(trojan_toggles))}")
print(f"KL Divergence (D_KL):  {kl_div:.6f} nats\n")
