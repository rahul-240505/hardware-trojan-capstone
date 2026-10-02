# Hardware Trojans in Battery-Powered Embedded Devices: Threat Models, Synthesis-Masking Quantification, and Analog State-Space Detection

**Author:** Rahul Kumar Mahato (Roll No: 123CS0183)  
**Supervisor:** Prof. Sumanta Pyne  
**Department of Computer Science and Engineering, National Institute of Technology Rourkela**  
**Session:** Autumn Semester 2026–27 (Capstone Project-I)

---

## Abstract
Battery-powered embedded devices—such as remote IoT sensor nodes and implantable medical devices (IMDs)—operate under stringent Size, Weight, and Power (SWaP) constraints and rely on deep-sleep states for multi-year battery longevity. Adversaries in untrusted foundries exploit third-party intellectual property (3PIP) cores to inject *Vampire Trojans*: stealthy hardware modifications that remain logically dormant during functional verification while draining energy during sleep modes. In this work, we demonstrate and quantify two fundamental barriers to post-silicon Trojan detection: (1) the **Synthesis-Masking Effect**, where aggressive Electronic Design Automation (EDA) optimization merges malicious logic into benign combinational cones, and (2) the **PVT Noise Barrier**, where Process, Voltage, and Temperature variations obscure sub-50-gate Trojan power signatures. Using an open-source 45nm NanGate EDA pipeline (`iverilog` and `Yosys`), we show that aggressive synthesis absorbs up to **100.0%** of Trojan gate overhead in control-centric benchmarks (`RS232`) and reduces Kullback-Leibler ($D_{KL}$) side-channel divergence by **92.31%**, pushing the Signal-to-Noise Ratio (SNR) down to **-10.90 dB** at 15% PVT noise. To overcome this limitation without incurring digital DSP power overhead, we formulate an **Analog State-Space RC Decay Monitor** ($\dot{\mathbf{x}}(t) = \mathbf{A}\mathbf{x}(t)$) that tracks passive decoupling-capacitor voltage decay during deep sleep, achieving **100.0% Monte Carlo detection accuracy** with a **156.45 mV** peak voltage anomaly at a power budget of **~38.5 nW**.

---

## 1. Threat Model: Sleep-Mode Vampire Attacks
Unlike functional Hardware Trojans that corrupt primary logical outputs, a **Vampire Trojan** targets the battery lifespan of SWaP-constrained nodes:
* **Trigger Mechanism:** A combinational comparator or sequential state detector taps shared internal buses (`0x7E` in Sensor Prototype, `0x99` parity frame in `RS232`, `0xDEAD` key state in `AES-T1800`) to arm a hidden latch without altering critical path timing.
* **Energy-Exhaustion Payload:** Activated strictly when `sleep_mode == 1`, driving a redundant linear-feedback shift register (LFSR) or sub-threshold leakage path that continuously dissipates dynamic and static power while primary outputs remain frozen in their benign sleep state.

---

## 2. Experimental Evaluation of Synthesis-Masking (45nm NanGate)

| Benchmark Circuit | Clean Gates | Unopt Trojan Gates | Masked Trojan Gates | Area Absorbed (%) | Clean Toggles | Unopt Toggles | Masked Toggles | Dynamic Overhead Masked (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Sensor Prototype** | 44 | 72 | 58 | **50.00%** | 6,493 | 14,848 | 12,985 | **22.30%** |
| **RS232 UART Core** | 163 | 193 | 163 | **100.00%** | 31,717 | 42,054 | 31,123 | **100.00%** |
| **AES-T1800 S-Box** | 161 | 201 | 196 | **12.50%** | 36,697 | 48,887 | 44,220 | **38.29%** |

### Key Structural Insights
1. **Complete Masking in Control/Checksum Logic (`RS232`):** Because the RS232 Vampire trigger shares parity and bitwise XOR trees with the UART transmitter, Yosys optimization passes (`flatten`, `share -aggressive`, `abc -dff`) completely dissolved the 30-gate Trojan into existing standard cells (`163 gates` total), driving the post-synthesis SNR to **-10.90 dB** under 15% PVT variation.
2. **Partial Masking in Nonlinear Crypto Logic (`AES-T1800`):** Nonlinear Galois Field $GF(2^8)$ S-Box structures resist full boolean absorption (`12.50%` gate reduction), yet sub-expression sharing still eliminates **4,667 parasitic gate toggles** (`38.29%` dynamic masking).

---

## 3. Mathematical Formulation of the Analog State-Space RC Monitor
During deep sleep (`sleep_mode == 1`), the main supply switch is briefly opened over a $1.5\ \mu\text{s}$ diagnostic window ($u(t) = 0$). The Power Distribution Network (PDN) is governed by the homogeneous state-space system:

$$\begin{bmatrix} \dot{V}_1(t) \\ \dot{V}_2(t) \end{bmatrix} = \begin{bmatrix} -\frac{G_{grid}}{C_1} & \frac{G_{grid}}{C_1} \\ \frac{G_{grid}}{C_2} & -\frac{G_{grid} + G_{leak}}{C_2} \end{bmatrix} \begin{bmatrix} V_1(t) \\ V_2(t) \end{bmatrix}$$

* **Eigenvalue Shift:** In a clean die ($R_{leak} = 8.0\text{ k}\Omega$), the dominant decay mode is $\lambda_1 = -9.96 \times 10^5\text{ s}^{-1}$. Under a Vampire attack ($R_{leak} = 5.2\text{ k}\Omega$), the eigenvalue shifts to $\lambda_1' = -1.53 \times 10^6\text{ s}^{-1}$.
* **Detection Performance:** Sampling the local cluster capacitor $V_2(t)$ at $t_{opt} = 0.80\ \mu\text{s}$ yields a **$156.45\text{ mV}$** voltage anomaly ($450.5\text{ mV}$ Clean vs. $294.0\text{ mV}$ Infected), achieving **100.0% classification accuracy** across 500 Monte Carlo PVT trials while consuming only **~38.5 nW** via an ultra-low-power clocked nanopower comparator.
