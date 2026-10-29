# Assignment 2 - Optimised Matrix Multiplication and Sparse Matrices

Big Data, Grado en Ciencia e Ingeniería de Datos, ULPGC (2026-2027).

Baseline reused from Assignment 1: the validated Java triple-loop (i-j-k) implementation
(`java/MatMul.java` in https://github.com/pblmll26/Assignment01_MelladoMartin_MatrixMultiplication),
now the `multiplyBasic` method of `java/Dense.java`. The dense input matrices are generated with the same
`generate.py` (seed 42) as in Assignment 1.

## Contents

| Path | What it is |
|---|---|
| `generate.py` | Creates the dense input matrices A and B in `data/` (seed 42, same as Assignment 1) |
| `java/Dense.java` | Part A: basic i-j-k, loop reordering i-k-j, cache blocking (block size 64) |
| `java/Sparse.java` | Part B: random sparse matrices, CSR conversion and CSR × CSR multiplication |
| `check.py` | Correctness tests |
| `run_benchmarks.py` | Runs Part A and Part B |
| `analyze.py` | Builds the summary tables and the figures |
| `results/dense_times.csv` | Raw Part A times, one row per repetition |
| `results/sparse_times.csv` | Raw Part B times with input and output nonzero counts |
| `results/runs.csv` | Status of every run (ok, error or timeout) |
| `results/dense_summary.csv`, `results/sparse_summary.csv` | Medians, IQR, speedups, nonzero counts and storage |
| `figures/` | Plots |

## Environment used

- CPU: AMD Ryzen 5 5625U (6 physical cores, 12 logical processors, 2.3 GHz base, 16 MB L3)
- RAM: 16 GB DDR4-3200
- OS: Windows 11 Home 10.0.26200
- Java: OpenJDK 21.0.12.1 (Eclipse Temurin), HotSpot 64-Bit Server VM, options `-Xmx4g`
- Python 3.11.9, numpy 2.2.6, pandas 3.0.1, matplotlib 3.10.6

All methods are sequential (one computation thread). No library is used inside any multiplication.

## How to reproduce

Run every command from this folder (the `data/`, `results/` and `figures/` folders must exist).

```
pip install numpy pandas matplotlib
python generate.py
javac -d java java/Dense.java java/Sparse.java
python check.py
python run_benchmarks.py
python analyze.py
```

`run_benchmarks.py` takes about 20 minutes and overwrites the CSV files in `results/`.

## Running one program by hand

```
java -cp java Dense <basic|ikj|blocked> data/A_100.txt data/B_100.txt 5 [output_file]
java -cp java Sparse <dense|sparse> <n> <density> <seed> 5 [output_file]
```

## Part A - dense methods

- `basic`: i-j-k, the Assignment 1 baseline. B is read by columns.
- `ikj`: the same operations with the loops reordered to i-k-j. The inner loop reads a row of B and a row of C, so both are read contiguously.
- `blocked`: i-k-j applied to 64 × 64 tiles, so that the tiles of A, B and C being used (3 × 32 KiB) stay in cache.

All three use the same input files, `double[][]` storage, the same timer and the same timed region.

## Part B - sparse matrices

- Sparsity = percentage of zero entries. Density = percentage of nonzero entries = 100 - sparsity.
- Generation: for each entry, in row-major order, two numbers are drawn from `java.util.Random`: `r` and `v`. The entry is `v` if `r < density`, otherwise 0. Nonzeros are therefore uniformly distributed with values in [0, 1). Seed 42 for A and 43 for B.
- Densities: 0.1, 1, 5, 10, 25, 50, 75 and 100 %. Sizes: n = 1000 and 2000.
- Storage format: CSR (row start indices, column indices, values), written by hand in `Sparse.java`. No sparse library is used.
- Multiplication: CSR × CSR row by row, accumulating each output row in a temporary dense row of length n, then storing its nonzeros in CSR.
- Both modes use the same logical matrices:
  - `dense`: the dense `ikj` method.
  - `sparse`: dense A and B are converted to CSR, then multiplied. The conversion time and the multiplication time are measured separately.
- Nonzero counts of A, B and C are reported for every repetition.

## Measurement protocol

- Timed region: allocation of the result plus the multiplication (and, separately, the CSR conversion). Reading or generating inputs is not timed.
- Timer: `System.nanoTime()`.
- 3 warm-up multiplications (not reported), then 5 measured repetitions in the same process.
- Summary: median and IQR.
- Memory metric: estimated array storage of A, B and C. Dense: 8 bytes per entry. CSR: 12 bytes per nonzero (8 for the value, 4 for the column index) plus 4 bytes per row start. JVM overhead is not included.
- Budget: 600 s per multiplication.
- Correctness: `numpy.allclose` with rtol = 1e-9 and atol = 1e-12 against NumPy (dense methods, plus identity and zero matrices), and CSR results against the dense method on the same matrices for densities 0, 1, 10, 50 and 100 %.
