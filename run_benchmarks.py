import subprocess

reps = 5
time_limit = (reps + 3) * 600

f = open("results/dense_times.csv", "w")
f.write("method,n,repetition,time_s,checksum\n")
f.close()

f = open("results/sparse_times.csv", "w")
f.write("mode,n,density,repetition,convert_s,multiply_s,nnz_a,nnz_b,nnz_c,checksum\n")
f.close()

f = open("results/runs.csv", "w")
f.write("part,method,n,density,status\n")
f.close()


def run(command, results_file, run_line):
    print(" ".join(command), flush=True)
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=time_limit)
        status = "ok"
        if result.returncode != 0:
            status = "error"
        f = open(results_file, "a")
        f.write(result.stdout)
        f.close()
    except subprocess.TimeoutExpired:
        status = "timeout"
    f = open("results/runs.csv", "a")
    f.write(run_line + "," + status + "\n")
    f.close()
    return status


for method in ["basic", "ikj", "blocked"]:
    for n in [100, 200, 400, 800, 1600]:
        command = ["java", "-Xmx4g", "-cp", "java", "Dense", method, "data/A_" + str(n) + ".txt", "data/B_" + str(n) + ".txt", str(reps)]
        status = run(command, "results/dense_times.csv", "dense," + method + "," + str(n) + ",1.0")
        if status != "ok":
            break

for n in [1000, 2000]:
    for density in [0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0]:
        for mode in ["dense", "sparse"]:
            command = ["java", "-Xmx4g", "-cp", "java", "Sparse", mode, str(n), str(density), "42", str(reps)]
            run(command, "results/sparse_times.csv", "sparse," + mode + "," + str(n) + "," + str(density))
