import numpy as np
import matplotlib.pyplot as plt

benchmarks = ["Sensor Node\n(Prototype)", "RS232 UART\n(Control Core)", "AES-T1800\n(Crypto S-Box)"]
clean_toggles = [6493, 31717, 36697]
unopt_toggles = [14848, 42054, 48887]
masked_toggles = [12985, 31123, 44220]

gate_absorption = [50.0, 100.0, 12.5]
toggle_reduction = [
    (14848 - 12985) / (14848 - 6493) * 100,
    100.0,
    (48887 - 44220) / (48887 - 36697) * 100
]

x = np.arange(len(benchmarks))
width = 0.25

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

ax1.bar(x - width, clean_toggles, width, label="Clean Baseline (45nm)", color="#2ecc71")
ax1.bar(x, unopt_toggles, width, label="Unoptimized Trojan", color="#e74c3c")
ax1.bar(x + width, masked_toggles, width, label="Synthesized-Masked Trojan", color="#3498db")
ax1.set_xticks(x)
ax1.set_xticklabels(benchmarks)
ax1.set_ylabel("Total 45nm Gate-Level Toggles")
ax1.set_title("Cross-Benchmark Gate-Level Switching Activity")
ax1.legend()
ax1.grid(True, axis="y", alpha=0.3)

ax2.bar(x - width/2, gate_absorption, width, label="Trojan Gate Area Absorbed (%)", color="#9b59b6")
ax2.bar(x + width/2, toggle_reduction, width, label="Trojan Switching Overhead Masked (%)", color="#f39c12")
ax2.set_xticks(x)
ax2.set_xticklabels(benchmarks)
ax2.set_ylim(0, 115)
ax2.set_ylabel("EDA Optimization Masking Percentage (%)")
ax2.set_title("Synthesis-Masking Efficacy: Linear Control vs. Nonlinear Crypto")
ax2.legend()
ax2.grid(True, axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("results_phase5_benchmarks.png", dpi=200)
print("Saved cross-benchmark summary chart to: results_phase5_benchmarks.png")
