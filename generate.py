import random

random.seed(42)

sizes = [2, 3, 10, 100, 200, 400, 800, 1600]

for n in sizes:
    for name in ["A", "B"]:
        f = open("data/" + name + "_" + str(n) + ".txt", "w")
        for i in range(n):
            row = []
            for j in range(n):
                row.append(str(random.random()))
            f.write(" ".join(row) + "\n")
        f.close()
    print("n =", n, "done")
