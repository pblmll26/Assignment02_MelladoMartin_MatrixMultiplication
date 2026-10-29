import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;

public class Dense {

    static final int BLOCK = 64;

    static double[][] readMatrix(String path) throws IOException {
        BufferedReader reader = new BufferedReader(new FileReader(path));
        ArrayList<double[]> rows = new ArrayList<>();
        String line = reader.readLine();
        while (line != null) {
            String[] parts = line.trim().split(" ");
            double[] row = new double[parts.length];
            for (int j = 0; j < parts.length; j++) {
                row[j] = Double.parseDouble(parts[j]);
            }
            rows.add(row);
            line = reader.readLine();
        }
        reader.close();
        double[][] matrix = new double[rows.size()][];
        for (int i = 0; i < rows.size(); i++) {
            matrix[i] = rows.get(i);
        }
        return matrix;
    }

    static double[][] multiplyBasic(double[][] A, double[][] B, int n) {
        double[][] C = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                double s = 0.0;
                for (int k = 0; k < n; k++) {
                    s += A[i][k] * B[k][j];
                }
                C[i][j] = s;
            }
        }
        return C;
    }

    static double[][] multiplyIkj(double[][] A, double[][] B, int n) {
        double[][] C = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int k = 0; k < n; k++) {
                double a = A[i][k];
                for (int j = 0; j < n; j++) {
                    C[i][j] += a * B[k][j];
                }
            }
        }
        return C;
    }

    static double[][] multiplyBlocked(double[][] A, double[][] B, int n) {
        double[][] C = new double[n][n];
        for (int ii = 0; ii < n; ii += BLOCK) {
            int iEnd = Math.min(ii + BLOCK, n);
            for (int kk = 0; kk < n; kk += BLOCK) {
                int kEnd = Math.min(kk + BLOCK, n);
                for (int jj = 0; jj < n; jj += BLOCK) {
                    int jEnd = Math.min(jj + BLOCK, n);
                    for (int i = ii; i < iEnd; i++) {
                        for (int k = kk; k < kEnd; k++) {
                            double a = A[i][k];
                            for (int j = jj; j < jEnd; j++) {
                                C[i][j] += a * B[k][j];
                            }
                        }
                    }
                }
            }
        }
        return C;
    }

    static double[][] multiply(String method, double[][] A, double[][] B, int n) {
        if (method.equals("basic")) {
            return multiplyBasic(A, B, n);
        }
        if (method.equals("ikj")) {
            return multiplyIkj(A, B, n);
        }
        return multiplyBlocked(A, B, n);
    }

    static double sum(double[][] C, int n) {
        double total = 0.0;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                total += C[i][j];
            }
        }
        return total;
    }

    static void writeMatrix(double[][] C, int n, String path) throws IOException {
        PrintWriter out = new PrintWriter(path);
        for (int i = 0; i < n; i++) {
            StringBuilder row = new StringBuilder();
            for (int j = 0; j < n; j++) {
                if (j > 0) {
                    row.append(" ");
                }
                row.append(C[i][j]);
            }
            out.println(row);
        }
        out.close();
    }

    public static void main(String[] args) throws IOException {
        String method = args[0];
        double[][] A = readMatrix(args[1]);
        double[][] B = readMatrix(args[2]);
        int reps = Integer.parseInt(args[3]);
        int n = A.length;
        int warmups = 3;

        for (int w = 0; w < warmups; w++) {
            multiply(method, A, B, n);
        }

        double[][] C = null;
        for (int r = 0; r < reps; r++) {
            long start = System.nanoTime();
            C = multiply(method, A, B, n);
            long end = System.nanoTime();
            double seconds = (end - start) / 1e9;
            System.out.println(method + "," + n + "," + (r + 1) + "," + seconds + "," + sum(C, n));
            System.out.flush();
        }

        if (args.length > 4) {
            writeMatrix(C, n, args[4]);
        }
    }
}
