# Hardware Trojans in Battery-Powered Embedded Devices: Threat Models, Detection, and Mitigation

**Candidate:** Rahul Kumar Mahato (123CS0183)  
**Supervisor:** Prof. Sumanta Pyne  
**Term:** Capstone Project-I (Autumn Semester 2026-27)

---

## 1. Overview & Problem Statement
Battery-powered edge IoT nodes and implantable medical devices (IMDs) operate under strict Size, Weight, and Power (SWaP) constraints and rely on deep-sleep states for multi-year battery longevity. Adversaries exploit untrusted foundries and 3PIP blocks to inject **Vampire Trojans**—stealthy hardware modifications that leave logical outputs untouched during standard verification while draining power during sleep states.

This repository contains the open-source Electronic Design Automation (EDA) simulation pipeline, synthesis-masking quantification scripts, and statistical side-channel models developed for this research.

---

## 2. Tech Stack & Open-Source EDA Toolchain
* **RTL Simulation:** Icarus Verilog (`iverilog` v12.0) & `vvp`
* **Logic Synthesis & Optimization:** Yosys (`v0.33`) + ABC
* **Technology Library:** NanGate 45nm Open Cell Library
* **Statistical & Side-Channel Analysis:** Python 3 (`numpy`, `scipy`, `vcdvcd`, `matplotlib`)

---

## 3. Repository Structure

    capstone_ht/
    ├── rtl/                  # Baseline and Trojan-infected Verilog RTL designs
    ├── tb/                   # Verification testbenches
    ├── netlist/              # Synthesized 45nm gate-level netlists (Yosys output)
    ├── scripts/              # Yosys synthesis scripts, library fetchers, and Python KL-divergence analyzers
    ├── lib/                  # NanGate 45nm Liberty (.lib) and gate-level (.v) models (auto-downloaded)
    └── vcd/                  # Value Change Dump (.vcd) switching activity traces

---

## 4. Progress Log & Experimental Walkthrough

### Phase 1: Baseline RTL vs. Vampire Trojan Injection (Completed)
* **Objective:** Design a sleep-enabled embedded sensor node (`rtl/sensor_clean.v`) and inject a dormant Vampire Trojan (`rtl/sensor_trojan.v`) triggered by a specific input vector (`0xDE`) that activates a parasitic switching load exclusively when `sleep_mode == 1`.
* **Verification:** Simulated 50 active clock cycles followed by 100 deep-sleep clock cycles (`tb/tb_sensor.v`). Functional outputs (`data_out`) matched 100% across both circuits.
* **Pre-Synthesis Statistical Results:**
  * **Clean Baseline Switching Toggles:** `959`
  * **Trojan-Infected Switching Toggles:** `1,082` (+123 parasitic toggles during sleep mode)
  * **Pre-Synthesis KL Divergence ($D_{KL}$):** `0.017049 nats` (under +/- 10% Gaussian PVT noise modeling)

**To reproduce Phase 1:**

    iverilog -DVCD_FILE=\"vcd/clean.vcd\" -o sim_clean rtl/sensor_clean.v tb/tb_sensor.v && vvp sim_clean
    iverilog -DVCD_FILE=\"vcd/trojan.vcd\" -o sim_trojan rtl/sensor_trojan.v tb/tb_sensor.v && vvp sim_trojan
    python3 scripts/analyze_kl.py

---

### Phase 2: Quantifying the Synthesis-Masking Effect (In Progress)
* **Objective:** Compile RTL into 45nm physical gates using Yosys under both unoptimized and aggressively flattened/shared synthesis passes to measure how EDA optimization absorbs Trojan logic and suppresses $D_{KL}$.
