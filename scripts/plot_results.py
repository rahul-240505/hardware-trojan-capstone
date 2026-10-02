import numpy as np
import matplotlib.pyplot as plt
from vcdvcd import VCDVCD

def extract_cycle_toggles(vcd_path, clock_period=10000, max_time=1500000):
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
cycles = np.arange(len(clean))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

ax1.plot(cycles, unopt, label="Unoptimized Infected Chip (14,848 toggles)", color="#e74c3c", alpha=0.8)
ax1.plot(cycles, masked, label="Synthesized-Masked Infected Chip (12,985 toggles)", color="#f39c12", linewidth=2)
ax1.plot(cycles, clean, label="Clean Baseline Chip (6,493 toggles)", color="#2ecc71", linewidth=2)
ax1.axvline(x=52, color="black", linestyle="--", label="Deep Sleep Mode Starts (Cycle 52)")
ax1.set_ylabel("Gate Toggles / Clock Cycle")
ax1.set_title("45nm Gate-Level Switching Activity: Clean vs. Vampire Trojan (Awake -> Sleep Mode)")
ax1.legend(loc="upper right")
ax1.grid(True, alpha=0.3)

ax2.fill_between(cycles, unopt - clean, color="#e74c3c", alpha=0.3, label="Unoptimized Trojan Footprint")
ax2.fill_between(cycles, masked - clean, color="#3498db", alpha=0.6, label="Post-Synthesis Masked Footprint (Yosys Optimized)")
ax2.axvline(x=52, color="black", linestyle="--")
ax2.set_xlabel("Clock Cycle (10ns period)")
ax2.set_ylabel("Extra Toggles vs. Clean")
ax2.set_title("Synthesis-Masking Effect: How Yosys Shrinks the Trojan Side-Channel Footprint")
ax2.legend(loc="upper right")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("results_phase1_2.png", dpi=200)
