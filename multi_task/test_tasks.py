import decimal
import argparse
import time
import sys
def is_prime(n):
    if n <= 1: return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0: return False
    return True

def calc_pi(precision):
    decimal.getcontext().prec = precision + 2
    C = 426880 * decimal.Decimal(10005).sqrt()
    M = 1
    L = 13591409
    X = 1
    K = 6
    S = L
    for i in range(1, precision//14 + 2):
        M = (K**3 - 16*K) * M // (i+1)**3
        L += 545140134
        X *= -262537412640768000
        S += decimal.Decimal(M * L) / X
        K += 12
    return C / S


def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)



import numpy as np

def matrix_ops(size):
    a = np.random.rand(size, size)
    b = np.random.rand(size, size)
    return np.linalg.det(a @ b)





def monte_carlo(samples):
    inside = 0
    for _ in range(samples):
        x, y = np.random.random(), np.random.random()
        if x**2 + y**2 <= 1:
            inside += 1
    return 4 * inside / samples



# 测试大数（示例参数可能需要调整）
# sum(is_prime(n) for n in range(1_000_000, 6_000_001))

# 示例：计算1000位圆周率（耗时约2-5分钟）
# calc_pi(25_000)

# 示例：2000x2000矩阵（需约2GB内存，耗时约3-5分钟）
# matrix_ops(2000)

# monte_carlo(30_000_000)

# 测试参数建议：n=35-40（指数级复杂度）
# fib(41)

def main():
    parser = argparse.ArgumentParser(description='数学计算任务执行器')
    subparsers = parser.add_subparsers(dest='task', required=True, help='任务类型')

    # 质数检测
    prime_parser = subparsers.add_parser('prime', help='质数检测')
    prime_parser.add_argument('start', type=int, help='起始值')
    prime_parser.add_argument('end', type=int, help='结束值')

    # 圆周率计算
    pi_parser = subparsers.add_parser('pi', help='计算圆周率')
    pi_parser.add_argument('precision', type=int, help='精度位数')

    # 斐波那契数列
    fib_parser = subparsers.add_parser('fib', help='斐波那契数列')
    fib_parser.add_argument('n', type=int, help='项数')

    # 矩阵运算
    matrix_parser = subparsers.add_parser('matrix', help='矩阵运算')
    matrix_parser.add_argument('size', type=int, help='矩阵维度')

    # 蒙特卡洛
    mc_parser = subparsers.add_parser('mc', help='蒙特卡洛积分')
    mc_parser.add_argument('samples', type=int, help='采样次数')

    args = parser.parse_args()

    try:
        start_time = time.time()
        if args.task == 'prime':
            count = sum(1 for n in range(args.start, args.end + 1) if is_prime(n))
            print(f"发现 {count} 个质数")

        elif args.task == 'pi':
            pi = calc_pi(args.precision)
            print(f"前50位: {str(pi)[:50]}...")

        elif args.task == 'fib':
            result = fib(args.n)
            print(f"fib({args.n}) = {result}")

        elif args.task == 'matrix':
            det = matrix_ops(args.size)
            print(f"行列式值: {det:.4e}")

        elif args.task == 'mc':
            pi_approx = monte_carlo(args.samples)
            print(f"π ≈ {pi_approx}")

        print(f"耗时 {time.time() - start_time:.2f}秒")
    except Exception as e:
        print(f"执行出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# # 质数检测
# python test_tasks.py prime 1000000 6000001
#
# # 计算圆周率
# python test_tasks.py pi 25000
#
# # 斐波那契
# python test_tasks.py fib 41
#
# # 矩阵运算（2000x2000）
# python test_tasks.py matrix 2000
#
# # 蒙特卡洛
# python test_tasks.py mc 30000000
