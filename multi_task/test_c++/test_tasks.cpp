#include <iostream>
#include <cmath>
#include <random>
#include <chrono>
#include <vector>
#include <iomanip>
using namespace std;

// 判断质数
bool is_prime(int n) {
    if (n <= 1) return false;
    for (int i = 2; i <= std::sqrt(n); ++i) {
        if (n % i == 0) return false;
    }
    return true;
}

// 计算圆周率
// 修复后的圆周率计算函数
//mpf_class calc_pi(int precision) {
//    mpf_set_default_prec(precision + 2);
//    mpf_class C = 426880 * sqrt(mpf_class(10005));
//    mpf_class M = 1;
//    mpf_class L = 13591409;
//    mpf_class X = 1;
//    mpf_class K = 6;
//    mpf_class S = L;
//
//    for (int i = 1; i <= precision / 14 + 2; ++i) {
//        M = (K * K * K - 16 * K) * M / ((i + 1) * (i + 1) * (i + 1));
//        L += 545140134;
//        X *= mpf_class(-262537412640768000);
//        S += M * L / X;
//        K += 12;
//    }
//
//    return C / S;
//}



long double calculate_pi_series(long long iterations) {
    long double pi = 0.0;
    int sign = 1;
    long long out_count = iterations /10;
    for (long long  i = 0; i < iterations; ++i) {
        long double term = 1.0 / (2*i + 1);
        pi += sign * term;
        sign *= -1; // 交替符号

        if (i % out_count == 0) { // 每百万次输出进度
            cout << "Iteration " << i
                 << ": π ≈ " <<std::setprecision(50) << 4*pi
                 << endl;
        }
    }
    return 4 * pi;
}



// 斐波那契数列
int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

// 矩阵运算
double matrix_ops(int size) {
    std::vector<std::vector<double>> a(size, std::vector<double>(size));
    std::vector<std::vector<double>> b(size, std::vector<double>(size));
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0, 1.0);

    for (int i = 0; i < size; ++i) {
        for (int j = 0; j < size; ++j) {
            a[i][j] = dis(gen);
            b[i][j] = dis(gen);
        }
    }

    std::vector<std::vector<double>> c(size, std::vector<double>(size, 0));
    for (int i = 0; i < size; ++i) {
        for (int j = 0; j < size; ++j) {
            for (int k = 0; k < size; ++k) {
                c[i][j] += a[i][k] * b[k][j];
            }
        }
    }

    double trace = 0;
    for (int i = 0; i < size; ++i) {
        trace += c[i][i];
    }
    return trace;
}

// 蒙特卡洛积分
double monte_carlo(int samples) {
    int inside = 0;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0, 1.0);

    for (int i = 0; i < samples; ++i) {
        double x = dis(gen);
        double y = dis(gen);
        if (x * x + y * y <= 1) {
            inside++;
        }
    }
    return 4.0 * inside / samples;
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <task> <args...>" << std::endl;
        return 1;
    }

    std::string task = argv[1];
    auto start_time = std::chrono::high_resolution_clock::now();

    try {
        if (task == "prime") {
            int start = std::stoi(argv[2]);
            int end = std::stoi(argv[3]);
            int count = 0;
            for (int n = start; n <= end; ++n) {
                if (is_prime(n)) count++;
            }
            std::cout << "发现 " << count << " 个质数" << std::endl;
        } else if (task == "pi") {
            long long precision = std::stoll(argv[2]);
            long double pi =  calculate_pi_series(precision);
            std::cout << std::setprecision(50) << pi; // 输出50位有效数字
            std::cout << "..." << std::endl;
        } else if (task == "fib") {
            int n = std::stoi(argv[2]);
            int result = fib(n);
            std::cout << "fib(" << n << ") = " << result << std::endl;
        } else if (task == "matrix") {
            int size = std::stoi(argv[2]);
            double det = matrix_ops(size);
            std::cout << "行列式值: " << std::scientific << std::setprecision(4) << det << std::endl;
        } else if (task == "mc") {
            int samples = std::stoi(argv[2]);
            double pi_approx = monte_carlo(samples);
            std::cout << "π ≈ " << pi_approx << std::endl;
        } else {
            std::cerr << "未知任务: " << task << std::endl;
            return 1;
        }

        auto end_time = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = end_time - start_time;
        std::cout << "耗时 " << elapsed.count() << " 秒" << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "执行出错: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}

//test_tasks mc 400000000
//test_tasks fib 48
//test_tasks prime 1000000 6000001
//test_tasks pi 5000000000