import subprocess

import numpy as np

A3 = np.loadtxt("data/A_3.txt")
np.savetxt("data/I_3.txt", np.identity(3), fmt="%.1f")
np.savetxt("data/Z_3.txt", np.zeros((3, 3)), fmt="%.1f")

tests = []
tests.append(["A_3 x I_3 = A_3", "data/A_3.txt", "data/I_3.txt", A3])
tests.append(["A_3 x Z_3 = 0", "data/A_3.txt", "data/Z_3.txt", np.zeros((3, 3))])
for n in [2, 3, 10, 100]:
    A = np.loadtxt("data/A_" + str(n) + ".txt", ndmin=2)
    B = np.loadtxt("data/B_" + str(n) + ".txt", ndmin=2)
    tests.append(["A_" + str(n) + " x B_" + str(n) + " vs NumPy", "data/A_" + str(n) + ".txt", "data/B_" + str(n) + ".txt", A @ B])

failed = 0

for method in ["basic", "ikj", "blocked"]:
    for test in tests:
        subprocess.run(["java", "-cp", "java", "Dense", method, test[1], test[2], "1", "results/check_output.txt"], stdout=subprocess.DEVNULL)
        result = np.loadtxt("results/check_output.txt", ndmin=2)
        ok = np.allclose(result, test[3], rtol=1e-9, atol=1e-12)
        if ok:
            print("PASS", method, test[0])
        else:
            print("FAIL", method, test[0])
            failed += 1

for density in [0.0, 0.01, 0.1, 0.5, 1.0]:
    subprocess.run(["java", "-cp", "java", "Sparse", "dense", "100", str(density), "7", "1", "results/check_dense.txt"], stdout=subprocess.DEVNULL)
    subprocess.run(["java", "-cp", "java", "Sparse", "sparse", "100", str(density), "7", "1", "results/check_sparse.txt"], stdout=subprocess.DEVNULL)
    expected = np.loadtxt("results/check_dense.txt")
    result = np.loadtxt("results/check_sparse.txt")
    ok = np.allclose(result, expected, rtol=1e-9, atol=1e-12)
    if ok:
        print("PASS sparse vs dense, density", density)
    else:
        print("FAIL sparse vs dense, density", density)
        failed += 1

print(failed, "tests failed")
