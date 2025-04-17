import multiprocessing

import psutil
import os


def get_cpu_info():
    # 获取当前进程关联的核心
    process = psutil.Process(os.getpid())
    allowed_cores = process.cpu_affinity()

    # 获取当前运行的核心（Windows/Linux实现不同）
    current_core = None
    if hasattr(os, 'sched_getcpu'):  # Linux/MacOS
        current_core = os.sched_getcpu()
    else:  # Windows
        from ctypes import windll
        current_core = windll.kernel32.GetCurrentProcessorNumber()

    # 获取系统总核心数
    total_cores = psutil.cpu_count(logical=True)

    return current_core, [c for c in range(total_cores) if c != current_core]


def worker_task(core_id, task_name):
    # 绑定到指定核心
    process = psutil.Process(os.getpid())
    try:
        process.cpu_affinity([core_id])
    except psutil.AccessDenied:
        print("权限不足，需要管理员/root权限")
    except Exception as e:
        print(f"核心绑定失败: {str(e)}")

    # 验证实际运行核心
    current_core = os.sched_getcpu() if hasattr(os, 'sched_getcpu') else \
        multiprocessing.current_process()._identity[0] % psutil.cpu_count()

    # 模拟计算任务
    result = 0
    for i in range(10_000_000):
        result += i % 100
    print(f"任务 {task_name} 在核心 {current_core} 完成，结果: {result}")


def create_tasks():
    # 获取可用核心
    _, available_cores = get_cpu_info()
    if len(available_cores) < 2:
        raise RuntimeError("至少需要两个可用CPU核心")

    # 选择前两个核心
    core1, core2 = available_cores[:2]

    # 创建进程
    p1 = multiprocessing.Process(
        target=worker_task,
        args=(core1, "A"),
        name="Core{}_Task".format(core1)
    )
    p2 = multiprocessing.Process(
        target=worker_task,
        args=(core2, "B"),
        name="Core{}_Task".format(core2)
    )

    # 启动并等待
    p1.start()
    p2.start()
    p1.join()
    p2.join()


if __name__ == "__main__":
    current, others = get_cpu_info()
    print(f"当前核心: {current}")
    print(f"其他核心: {others}")
    create_tasks()

