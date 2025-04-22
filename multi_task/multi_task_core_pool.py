import datetime
import multiprocessing
import subprocess
import psutil
import os
from ctypes import windll  # Windows核心获取需要
import matplotlib
matplotlib.use('Agg')  # 在导入pyplot之前设置非交互式后端
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

def plot_timeline(task_history, filename="task_timeline.png"):
    print(f"任务 {task_history} ")
    plt.figure(figsize=(12, len(task_history) * 0.5 + 2))

    # 转换时间格式
    min_time = min(t['start'] for t in task_history)
    max_time = max(t['end'] for t in task_history)
    print(f"时间范围: {min_time} - {max_time}")

    for i, task in enumerate(task_history):
        # 计算相对时间位置
        start = (task['start'] - min_time).total_seconds()
        duration = (task['end'] - task['start']).total_seconds()

        bar_container = plt.barh(
            y=f"Core {task['core']}",
            width=duration,
            left=start,
            height=0.6,
            label=task['cmd']
            # label=str(i)
        )
        bar = bar_container.patches[0]
        y_center = bar.get_y() + bar.get_height() / 2
        plt.text(start + duration / 2, y_center, str(i),
                 ha='center', va='center', color='white')

    # 设置时间轴格式
    # plt.gca().xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
    # plt.gca().xaxis_date()  # 声明X轴使用日期格式
    # plt.xlim(min_time, max_time)  # 显式设置时间范围
    plt.xlabel(f"Time ({min_time.strftime('%Y-%m-%d')})")
    plt.tight_layout()
    plt.savefig(filename)
    print(f"运行时间线已保存至 {filename}")


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


def worker_loop(core_id, task_queue, task_history):

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
            index, cmd_args = task_queue.get(block=True, timeout=5)
        except multiprocessing.queues.Empty:
            # 队列持续空置5秒后退出
            break

        # 执行任务
        start_time = datetime.datetime.now()
        current_core = os.sched_getcpu() if hasattr(os, 'sched_getcpu') else core_id
        print(f"time:{start_time} 任务 [{index}] {cmd_args} 在核心 {current_core} 开始")
        start_time = datetime.datetime.now()
        # 记录任务元数据
        task_data = {
            "core": core_id,
            "cmd": cmd_args,
            "start": start_time,
            "end": datetime.datetime.now()  # 最后更新真实结束时间
        }
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            encoding='utf-8',
            shell=True  # 允许执行shell命令
        )

        end_time = datetime.datetime.now()
        duration = end_time - start_time
        task_data["end"] = end_time
        print(f"time:{end_time} 任务 {cmd_args} 在核心 {current_core} 结束 : {result.stderr}")
        print(f"任务总耗时: {duration}")
        task_history.append(task_data)


def create_tasks(command_args):
    """创建核心池执行任务"""
    task_queue = multiprocessing.Queue()
    manager = multiprocessing.Manager()
    task_history = manager.list()

    # 填充任务队列
    for idx, cmd in enumerate(command_args["commands"]):
        task_queue.put((idx, cmd["cmd"]))

    # 创建核心池进程
    processes = []
    for core_id in selected_cores:
        p = multiprocessing.Process(
            target=worker_loop,
            args=(core_id, task_queue, task_history),
            name=f"Core{core_id}_Worker"
        )
        processes.append(p)
        p.start()

    # 等待所有工作进程完成
    for p in processes:
        p.join()

    plot_timeline(list(task_history),
                filename=f"task_timeline_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.png")

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
            {"cmd": f"c:/python/python310/python.exe test_tasks.py prime 1000000 20000001"},
            {"cmd": f"c:/python/python310/python.exe test_tasks.py pi 10000"},
            {"cmd": f"c:/python/python310/python.exe test_tasks.py fib 21"},
            {"cmd": f"c:/python/python310/python.exe test_tasks.py matrix 1000"},
            {"cmd": f"c:/python/python310/python.exe test_tasks.py mc 3000000"},
        ]
    }

    # 执行任务
    create_tasks(demo_commands)
