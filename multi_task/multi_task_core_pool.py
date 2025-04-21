import datetime
import multiprocessing
import subprocess
import psutil
import os
from ctypes import windll  # Windows核心获取需要


def get_cpu_info():
    """获取CPU核心信息"""
    process = psutil.Process(os.getpid())
    allowed_cores = process.cpu_affinity()

    # 获取当前运行核心
    current_core = None
    if hasattr(os, 'sched_getcpu'):  # Linux/MacOS
        current_core = os.sched_getcpu()
    else:  # Windows
        current_core = windll.kernel32.GetCurrentProcessorNumber()

    # 获取系统总核心数
    total_cores = psutil.cpu_count(logical=True)
    return current_core, [c for c in range(total_cores) if c != current_core]


def worker_loop(core_id, task_queue):
    """核心工作循环"""
    process = psutil.Process(os.getpid())
    try:
        process.cpu_affinity([core_id])
        print(f"核心 {core_id} 绑定成功")
    except Exception as e:
        print(f"核心 {core_id} 绑定失败: {e}")
        return

    while True:
        try:
            # 从队列获取任务（5秒超时检测）
            cmd_args = task_queue.get(block=True, timeout=5)
        except multiprocessing.queues.Empty:
            # 队列持续空置5秒后退出
            break

        # 执行任务
        start_time = datetime.datetime.now()
        current_core = os.sched_getcpu() if hasattr(os, 'sched_getcpu') else core_id
        print(f"time:{start_time} 任务 {cmd_args} 在核心 {current_core} 开始")

        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            shell=True  # 允许执行shell命令
        )

        end_time = datetime.datetime.now()
        duration = end_time - start_time
        print(f"time:{end_time} 任务 {cmd_args} 在核心 {current_core} 结束 : {result.stderr}")
        print(f"任务总耗时: {duration}")


def create_tasks(command_args):
    """创建核心池执行任务"""
    task_queue = multiprocessing.Queue()

    # 填充任务队列
    for cmd in command_args["commands"]:
        task_queue.put(cmd["cmd"])

    # 创建核心池进程
    processes = []
    for core_id in selected_cores:
        p = multiprocessing.Process(
            target=worker_loop,
            args=(core_id, task_queue),
            name=f"Core{core_id}_Worker"
        )
        processes.append(p)
        p.start()

    # 等待所有工作进程完成
    for p in processes:
        p.join()


if __name__ == "__main__":
    # 初始化核心池
    current, others = get_cpu_info()
    max_core_limit = 3
    selected_cores = others[:max_core_limit]

    print(f"当前核心: {current}")
    print(f"可用核心池: {selected_cores}")

    # 任务配置（使用列表格式更安全）
    demo_commands = {
        "commands": [
            # {"cmd": [f"c:/python/python310/python.exe", "test_tasks.py", "prime", "1000000", "6000001"]},
            # {"cmd": [f"c:/python/python310/python.exe", "test_tasks.py", "pi", "25000"]},
            # {"cmd": [f"c:/python/python310/python.exe", "test_tasks.py", "fib", "41"]},
            # {"cmd": [f"c:/python/python310/python.exe", "test_tasks.py", "matrix", "2000"]},
            # {"cmd": [f"c:/python/python310/python.exe", "test_tasks.py", "mc", "30000000"]},
            {"cmd": f"c:/python/python310/python.exe test_tasks.py prime 1000000 6000001"},
            {"cmd": f"c:/python/python310/python.exe test_tasks.py pi 25000"},
            {"cmd": f"c:/python/python310/python.exe test_tasks.py fib 41"},
            {"cmd": f"c:/python/python310/python.exe test_tasks.py matrix 000"},
            {"cmd": f"c:/python/python310/python.exe test_tasks.py mc 30000000"},
        ]
    }

    # 执行任务
    create_tasks(demo_commands)
