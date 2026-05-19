# The Energy Landscape of Python Libraries: A Cross-Domain Empirical Study
### Replication Package — ESEM 2026 Submission

This repository contains the measurement scripts, raw RAPL data, analysis code,
and input fixtures for the paper *"The Energy Landscape of Python Libraries:
A Cross-Domain Empirical Study"* submitted to ESEM 2026.

The study benchmarks energy consumption of 13 Python libraries across three domains
(serialization, image processing, data processing) using
[SLEM](https://rishalab.github.io/SLEM/) as a uniform measurement instrument
built atop Intel RAPL.

---

## Repository Structure

```
.
├── README.md                        # This file
│
├── -- Input Fixtures --
├── generate_fixtures.py             # Regenerates all input fixtures from scratch
├── img_512.jpg                      # Image fixture — 512 px RGB (small workload)
├── img_2048.jpg                     # Image fixture — 2048 px RGB (large workload)
├── payload_100KB.json               # Serialization fixture — 100 KB JSON payload
├── payload_10MB.json                # Serialization fixture — 10 MB JSON payload
│
├── -- Experiment Execution --
├── run_batch_experiments.py         # Master script: runs all domains, all libraries
│
├── -- Analysis --
├── analyze_rqs.py                   # Wilcoxon, Cliff's delta, Friedman, Holm correction
├── debug_csv.py                     # Validates raw CSV: missing runs, CV flags, wrap-around
│
├── -- Session Log --
├── slem_overnight.log               # Full log from the overnight experiment session
│
├── evaluation/
│   ├── evaluation_scripts/
│   │   ├── measure_serialization.py # Measures json, orjson, ujson at 100KB and 10MB
│   │   ├── measure_image.py         # Measures OpenCV and Pillow resize at 512px and 2048px
│   │   ├── measure_data.py          # Measures Pandas and Polars dropna (dispatcher)
│   │   ├── measure_adult.py         # Measures Pandas/Polars on Adult dataset (~32k rows)
│   │   └── measure_us_census.py     # Measures Pandas/Polars on US Census dataset (~2.4M rows)
│   │
│   └── evaluation_results/
│       ├── measure_serialization_json_100KB.csv
│       ├── measure_serialization_json_10MB.csv
│       ├── measure_serialization_orjson_100KB.csv
│       ├── measure_serialization_orjson_10MB.csv
│       ├── measure_serialization_ujson_100KB.csv
│       ├── measure_serialization_ujson_10MB.csv
│       ├── measure_image_cv2_resize_512.csv
│       ├── measure_image_cv2_resize_2048.csv
│       ├── measure_image_pil_resize_512.csv
│       ├── measure_image_pil_resize_2048.csv
│       ├── measure_data_pandas_dropna.csv
│       ├── measure_data_polars_dropna.csv
│       ├── adult/                   # Raw RAPL CSVs for all tasks on Adult dataset
│       └── us_census/               # Raw RAPL CSVs for all tasks on US Census dataset
│
└── src/                             # SLEM tool source
    ├── main.py                      # Entry point (launches GUI)
    ├── gui.py                       # Tkinter GUI frontend
    ├── energy_measure.py            # RAPL reads via Linux powercap interface
    ├── runner.py                    # Execution loop: pre/post reads, CSV persistence
    ├── init.config                  # Idle gap, warm-up count, core pinning settings
    └── module.config                # Library registry used by batch experiments
```

---

## Hardware and Software Requirements

### Hardware
- **Processor:** Intel CPU with RAPL support (Sandy Bridge or newer:
  Core i3/i5/i7/i9, Xeon series)
- **RAM:** 16 GB minimum; 128 GB recommended for US Census workloads at 2.4M rows
- **OS:** Ubuntu 22.04 LTS (kernel 5.15 used in the paper)
- Bare-metal only. RAPL is unavailable inside VMware, VirtualBox, or other hypervisors.
- RAPL is Intel-specific. AMD and ARM platforms are not supported by this tool.

### Software
```bash
pip install -r requirements.txt
```
All library versions are pinned in `requirements.txt`, generated via `pip freeze`
after the experiments were completed.

---

## System Preparation (Run Once Before Any Experiment Session)

Energy measurements are sensitive to background noise, frequency scaling, and thermal
drift. The following steps were applied in the paper and must be reproduced for
comparable results.

```bash
# 1. Set headless boot target (no GUI overhead)
sudo systemctl set-default multi-user.target
# Reboot after this step before proceeding.

# 2. Disable background services that generate periodic CPU activity
sudo systemctl mask packagekit unattended-upgrades cron anacron \
  accounts-daemon ModemManager bluetooth cups \
  avahi-daemon apport whoopsie

# 3. Fix CPU frequency and disable Intel Turbo Boost
#    (variable frequency is the largest noise source in RAPL)
sudo cpupower frequency-set -g performance
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo

# 4. Disable hyperthreading (SMT introduces unpredictable shared-core energy)
echo off | sudo tee /sys/devices/system/cpu/smt/control

# 5. Disable ASLR (improves run-to-run cache reproducibility)
echo 0 | sudo tee /proc/sys/kernel/randomize_va_space

# 6. Disable deep C-states (prevents cold-start vs. warm-start confounds)
#    Add intel_idle.max_cstate=1 to GRUB_CMDLINE_LINUX_DEFAULT in /etc/default/grub
#    then run: sudo update-grub && sudo reboot

# 7. Grant RAPL read access
sudo chmod -R +r /sys/class/powercap/
```

**Thermal stabilization:** Before the first measurement session, run a 60-second
warm-up workload and confirm that CPU package temperature is stable (less than 5°C
drift). `run_batch_experiments.py` logs temperature every 10 seconds to
`slem_overnight.log` and will warn if drift exceeds the threshold.

---

## Input Fixtures

All fixtures used in the paper are checked into the repository:

| File | Domain | Description |
|---|---|---|
| `payload_100KB.json` | Serialization | 100 KB flat + nested JSON payload |
| `payload_10MB.json` | Serialization | 10 MB flat + nested JSON payload |
| `img_512.jpg` | Image processing | 512 px RGB image (3 channels, 8-bit) |
| `img_2048.jpg` | Image processing | 2048 px RGB image (3 channels, 8-bit) |
| `evaluation/evaluation_results/adult/` | Data processing | Adult dataset (~32k rows) |
| `evaluation/evaluation_results/us_census/` | Data processing | US Census dataset (~2.4M rows) |

The Adult and US Census datasets are sourced from the UCI Machine Learning Repository
and cannot be redistributed. Download them before running data processing experiments:
- Adult dataset: https://archive.ics.uci.edu/dataset/2/adult
- US Census dataset: https://archive.ics.uci.edu/dataset/116/us+census+data+1990

Place the downloaded files inside the respective subdirectories under
`evaluation/evaluation_results/`.

To regenerate the serialization and image fixtures from scratch and verify SHA-256
hashes:
```bash
python generate_fixtures.py
sha256sum -c fixtures_hashes.txt
```

---

## Running the Experiments

### Full Batch Run (all domains, all libraries, ~12 hours)

```bash
taskset --cpu-list 0-3 nice -n -20 python run_batch_experiments.py
```

This executes all three domains sequentially:

| Domain | Libraries | Workloads | Runs |
|---|---|---|---|
| Serialization | json, orjson, ujson, msgpack, protobuf | 1KB/100KB/10MB × flat/nested | 600 |
| Image processing | OpenCV, Pillow, scikit-image, imageio | read/resize/blur/Sobel × 512px/2048px | 640 |
| Data processing | Pandas, Polars, DuckDB, Modin | 8 tasks × Adult + US Census | 640 |
| **Total** | | | **1,880** |

An additional 2 warm-up runs per cell are executed and discarded (2,256 total
executions; only 1,880 are analyzed).

**Per-run protocol applied automatically:**
- Run order is randomized within each (library, workload) cell and across cells
- 30-second idle gap between runs
- RAPL is read immediately before and after each function call; no polling during execution
- Each run is appended as one row to the raw CSV; no live aggregation
- CV is computed after each cell of 20 runs; cells with CV > 15% on PKG energy
  are flagged in the log and re-run once

Raw output is appended to `evaluation/evaluation_results/` using the naming
convention:

```
measure_<domain>_<library>_<workload>.csv
```

Each CSV row contains:

```
timestamp, domain, library, workload, run_index,
PKG_uJ, DRAM_uJ, Core_uJ, Uncore_uJ,
wall_time_ns, CPU_temp_C, governor_freq_MHz
```

### Per-Domain Runs

To run a single domain independently:
```bash
# Serialization only
python evaluation/evaluation_scripts/measure_serialization.py

# Image processing only
python evaluation/evaluation_scripts/measure_image.py

# Data processing — Adult dataset
python evaluation/evaluation_scripts/measure_adult.py

# Data processing — US Census dataset
python evaluation/evaluation_scripts/measure_us_census.py
```

Results are written to the corresponding files under `evaluation/evaluation_results/`.

---

## Statistical Analysis

```bash
python analyze_rqs.py
```

Reads all CSVs under `evaluation/evaluation_results/` and produces:

| Output | Content |
|---|---|
| RQ1 | Pairwise Wilcoxon p-values and Cliff's delta (95% CI) for all library pairs |
| RQ2 | Energy growth factors across workload sizes per library per domain |
| RQ3 | Native-backend vs. pure-Python comparisons across all three domains |
| RQ4 | Cross-domain ranking table; checks for domain-specific reversals |

Effect size thresholds follow Romano et al. (2006):
negligible < 0.147 / small < 0.33 / medium < 0.474 / large ≥ 0.474.

All pairwise tests are corrected using Holm-Bonferroni within each domain.

Box-plots with individual run points and Cliff's delta heatmaps are saved to
`figures/` (created on first run).

---

## Validating Raw CSV Output

```bash
python debug_csv.py
```

Scans all CSVs under `evaluation/evaluation_results/` and reports:
- Missing runs per cell (expected: exactly 20 per cell)
- Cells flagged for CV > 15% on PKG energy
- Zero-value or RAPL wrap-around anomalies
- Column completeness

---

## Pre-Collected Results

The `evaluation/evaluation_results/` directory already contains the raw RAPL CSVs
from the experiment run reported in the paper. A reviewer with different hardware
can inspect these files and run `analyze_rqs.py` directly without re-running
experiments.

The key result files corresponding to the paper's main findings are:

| File | Paper result |
|---|---|
| `measure_serialization_json_10MB.csv` | json: 3.7535 J at 10 MB |
| `measure_serialization_orjson_10MB.csv` | orjson: 1.2691 J at 10 MB (66.2% reduction) |
| `measure_serialization_ujson_10MB.csv` | ujson: 2.0066 J at 10 MB |
| `measure_image_cv2_resize_2048.csv` | OpenCV: 0.4162 J at 2048 px |
| `measure_image_pil_resize_2048.csv` | Pillow: 4.9717 J at 2048 px (11.9× gap) |
| `measure_data_pandas_dropna.csv` | Pandas dropna: 0.3605 J |
| `measure_data_polars_dropna.csv` | Polars dropna: 0.3388 J (6.0% reduction) |

---

## Session Log

`slem_overnight.log` is the full log from the overnight experiment run reported
in the paper. It contains timestamped entries for:
- CPU package temperature (every 10 seconds)
- Library versions at session start (`pip freeze` output)
- Per-cell CV values and any re-run events
- Hostname, kernel version, Python version
