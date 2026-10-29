import java.io.IOException;
import java.util.Arrays;
import java.util.Random;

public class Sparse {

    static class Csr {
        int n;
        int[] rowStart;
        int[] cols;
        double[] values;
    }

    static double[][] generate(int n, double density, long seed) {
        Random random = new Random(seed);
        double[][] m = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                double r = random.nextDouble();
                double v = random.nextDouble();
                if (r < density) {
                    m[i][j] = v;
                }
            }
        }
        return m;
    }

    static int countNonZeros(double[][] m, int n) {
        int count = 0;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (m[i][j] != 0.0) {
                    count++;
                }
            }
        }
        return count;
    }

    static Csr toCsr(double[][] d, int n) {
        int count = countNonZeros(d, n);
        Csr m = new Csr();
        m.n = n;
        m.rowStart = new int[n + 1];
        m.cols = new int[count];
        m.values = new double[count];
        int p = 0;
        for (int i = 0; i < n; i++) {
            m.rowStart[i] = p;
            for (int j = 0; j < n; j++) {
                if (d[i][j] != 0.0) {
                    m.cols[p] = j;
                    m.values[p] = d[i][j];
                    p++;
                }
            }
        }
        m.rowStart[n] = p;
        return m;
    }

    static Csr multiplySparse(Csr A, Csr B) {
        int n = A.n;
        Csr C = new Csr();
        C.n = n;
        C.rowStart = new int[n + 1];
        C.cols = new int[n];
        C.values = new double[n];
        double[] row = new double[n];
        int p = 0;
        for (int i = 0; i < n; i++) {
            C.rowStart[i] = p;
            for (int a = A.rowStart[i]; a < A.rowStart[i + 1]; a++) {
                int k = A.cols[a];
                for (int b = B.rowStart[k]; b < B.rowStart[k + 1]; b++) {
                    row[B.cols[b]] += A.values[a] * B.values[b];
                }
            }
            for (int j = 0; j < n; j++) {
                if (row[j] != 0.0) {
                    if (p == C.cols.length) {
                        C.cols = Arrays.copyOf(C.cols, p * 2);
                        C.values = Arrays.copyOf(C.values, p * 2);
                    }
                    C.cols[p] = j;
                    C.values[p] = row[j];
                    p++;
                    row[j] = 0.0;
                }
            }
        }
        C.rowStart[n] = p;
        return C;
    }

    static double[][] toDense(Csr m) {
        double[][] d = new double[m.n][m.n];
        for (int i = 0; i < m.n; i++) {
            for (int p = m.rowStart[i]; p < m.rowStart[i + 1]; p++) {
                d[i][m.cols[p]] = m.values[p];
            }
        }
        return d;
    }

    public static void main(String[] args) throws IOException {
        String mode = args[0];
        int n = Integer.parseInt(args[1]);
        double density = Double.parseDouble(args[2]);
        long seed = Long.parseLong(args[3]);
        int reps = Integer.parseInt(args[4]);
        int warmups = 3;

        double[][] A = generate(n, density, seed);
        double[][] B = generate(n, density, seed + 1);
        int nnzA = countNonZeros(A, n);
        int nnzB = countNonZeros(B, n);
        double[][] result = null;

        if (mode.equals("dense")) {
            for (int w = 0; w < warmups; w++) {
                Dense.multiplyIkj(A, B, n);
            }
            for (int r = 0; r < reps; r++) {
                long start = System.nanoTime();
                double[][] C = Dense.multiplyIkj(A, B, n);
                long end = System.nanoTime();
                double seconds = (end - start) / 1e9;
                int nnzC = countNonZeros(C, n);
                System.out.println("dense," + n + "," + density + "," + (r + 1) + ",0," + seconds + "," + nnzA + "," + nnzB + "," + nnzC + "," + Dense.sum(C, n));
                System.out.flush();
                result = C;
            }
        }

        if (mode.equals("sparse")) {
            for (int w = 0; w < warmups; w++) {
                multiplySparse(toCsr(A, n), toCsr(B, n));
            }
            for (int r = 0; r < reps; r++) {
                long start = System.nanoTime();
                Csr a = toCsr(A, n);
                Csr b = toCsr(B, n);
                long middle = System.nanoTime();
                Csr C = multiplySparse(a, b);
                long end = System.nanoTime();
                double convertSeconds = (middle - start) / 1e9;
                double multiplySeconds = (end - middle) / 1e9;
                double[][] dense = toDense(C);
                System.out.println("sparse," + n + "," + density + "," + (r + 1) + "," + convertSeconds + "," + multiplySeconds + "," + nnzA + "," + nnzB + "," + C.rowStart[n] + "," + Dense.sum(dense, n));
                System.out.flush();
                result = dense;
            }
        }

        if (args.length > 5) {
            Dense.writeMatrix(result, n, args[5]);
        }
    }
}
