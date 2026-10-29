import matplotlib.pyplot as plt
import pandas as pd

dense = pd.read_csv("results/dense_times.csv")
sparse = pd.read_csv("results/sparse_times.csv")

rows = []
for method in ["basic", "ikj", "blocked"]:
    for n in [100, 200, 400, 800, 1600]:
        values = dense[(dense["method"] == method) & (dense["n"] == n)]["time_s"]
        basic = dense[(dense["method"] == "basic") & (dense["n"] == n)]["time_s"]
        median = values.median()
        iqr = values.quantile(0.75) - values.quantile(0.25)
        speedup = basic.median() / median
        storage = 3 * 8 * n * n / 1024 / 1024
        rows.append([method, n, len(values), median, iqr, speedup, storage])
dense_summary = pd.DataFrame(rows, columns=["method", "n", "repetitions", "median_s", "iqr_s", "speedup_vs_basic", "storage_mib"])
dense_summary.to_csv("results/dense_summary.csv", index=False)
print(dense_summary.to_string(index=False))
print()

rows = []
for n in [1000, 2000]:
    for density in [0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0]:
        for mode in ["dense", "sparse"]:
            part = sparse[(sparse["mode"] == mode) & (sparse["n"] == n) & (sparse["density"] == density)]
            multiply = part["multiply_s"]
            convert = part["convert_s"]
            nnz_a = part["nnz_a"].iloc[0]
            nnz_b = part["nnz_b"].iloc[0]
            nnz_c = part["nnz_c"].iloc[0]
            if mode == "dense":
                storage = 3 * 8 * n * n
            else:
                storage = 12 * (nnz_a + nnz_b + nnz_c) + 3 * 4 * (n + 1)
            output_density = 100 * nnz_c / (n * n)
            iqr = multiply.quantile(0.75) - multiply.quantile(0.25)
            rows.append([n, density, mode, len(part), multiply.median(), iqr, convert.median(), nnz_a, nnz_b, nnz_c, output_density, storage / 1024 / 1024])
sparse_summary = pd.DataFrame(rows, columns=["n", "density", "mode", "repetitions", "multiply_median_s", "multiply_iqr_s", "convert_median_s", "nnz_a", "nnz_b", "nnz_c", "output_density_pct", "storage_mib"])
sparse_summary.to_csv("results/sparse_summary.csv", index=False)
print(sparse_summary.to_string(index=False))

plt.figure(figsize=(7, 5))
plt.plot([100, 200, 400, 800, 1600], dense_summary[dense_summary["method"] == "basic"]["median_s"], color="#2a78d6", marker="o", linewidth=2, label="basic (i-j-k)")
plt.plot([100, 200, 400, 800, 1600], dense_summary[dense_summary["method"] == "ikj"]["median_s"], color="#eb6834", marker="s", linewidth=2, label="loop reordering (i-k-j)")
plt.plot([100, 200, 400, 800, 1600], dense_summary[dense_summary["method"] == "blocked"]["median_s"], color="#1baf7a", marker="^", linewidth=2, label="cache blocking (64)")
plt.xscale("log")
plt.yscale("log")
plt.minorticks_off()
plt.xticks([100, 200, 400, 800, 1600], ["100", "200", "400", "800", "1600"])
plt.xlabel("Matrix size n (n × n)")
plt.ylabel("Median time per multiplication (s)")
plt.title("Dense methods in Java (median of 5 repetitions)")
plt.grid(True, color="#dddddd")
plt.legend()
plt.tight_layout()
plt.savefig("figures/dense_time.png", dpi=150)

densities = [0.1, 1, 5, 10, 25, 50, 75, 100]

for n in [1000, 2000]:
    d = sparse_summary[(sparse_summary["n"] == n) & (sparse_summary["mode"] == "dense")]
    s = sparse_summary[(sparse_summary["n"] == n) & (sparse_summary["mode"] == "sparse")]

    plt.figure(figsize=(7, 5))
    plt.plot(densities, d["multiply_median_s"], color="#eb6834", marker="s", linewidth=2, label="dense i-k-j")
    plt.plot(densities, s["multiply_median_s"], color="#eda100", marker="o", linewidth=2, label="CSR multiplication")
    plt.plot(densities, s["multiply_median_s"] + s["convert_median_s"], color="#e87ba4", marker="D", linewidth=2, linestyle="--", label="CSR multiplication + conversion")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Input density (% nonzero entries)")
    plt.ylabel("Median time (s)")
    plt.title("CSR vs dense multiplication, n = " + str(n) + " (median of 5 repetitions)")
    plt.grid(True, color="#dddddd")
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/sparse_time_" + str(n) + ".png", dpi=150)

    plt.figure(figsize=(7, 5))
    plt.plot(densities, d["storage_mib"], color="#eb6834", marker="s", linewidth=2, label="dense arrays (A, B, C)")
    plt.plot(densities, s["storage_mib"], color="#eda100", marker="o", linewidth=2, label="CSR arrays (A, B, C)")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Input density (% nonzero entries)")
    plt.ylabel("Estimated array storage (MiB)")
    plt.title("Storage of A, B and C, n = " + str(n))
    plt.grid(True, color="#dddddd")
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/sparse_memory_" + str(n) + ".png", dpi=150)
