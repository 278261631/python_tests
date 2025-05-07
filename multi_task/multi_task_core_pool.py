import datetime
import multiprocessing
import signal
import subprocess
import sys
from logging.handlers import RotatingFileHandler

import portalocker
import psutil
import os

import matplotlib
matplotlib.use('Agg')  # 在导入pyplot之前设置非交互式后端
import matplotlib.pyplot as plt

import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)
# logger.setLevel(logging.WARNING)

# 控制台Handler（INFO级别）
console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
console_handler.setLevel(logging.WARNING)

os.makedirs('log_core_pool', exist_ok=True)
os.makedirs('img_core_pool', exist_ok=True)
# 文件Handler（DEBUG级别）
file_handler = RotatingFileHandler(
    f'log_core_pool/task_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
    maxBytes=10*1024*1024,
    backupCount=30,
    encoding='utf-8'
)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

def plot_timeline(task_history, filename="task_timeline.png"):
    logging.info(f"任务 {task_history} ")
    if not task_history:
        logging.error("task_history = 0  无法生成时间线图表 - 任务历史记录为空")
        return
    plt.figure(figsize=(12, len(task_history) * 0.5 + 2))

    # 转换时间格式
    min_time = min(t['start'] for t in task_history)
    max_time = max(t['end'] for t in task_history)
    logging.warning(f"时间范围: {min_time} - {max_time}")

    for i, task in enumerate(task_history):
        # 计算相对时间位置
        start = (task['start'] - min_time).total_seconds()
        duration = (task['end'] - task['start']).total_seconds()
        logging.warning(f"任务 {task['main_id']}_{task['sub_id']} 开始时间: {start}  duration [{duration}]")
        duration = max(duration, 2)
        bar_container = plt.barh(
            y=f"Core {task['core']}",
            width=duration,
            left=start,
            height=0.3,
            alpha=0.5,
            label=f"Task {i}_{task['sub_id']}: {task['cmd']}"
            # label=str(i)
        )
        bar = bar_container.patches[0]
        y_center = bar.get_y() + bar.get_height() / 2
        plt.text(start + duration / 2, y_center, f"{task['main_id']}_{task['sub_id']}",
                 ha='center', va='center', color='white')

    # 设置时间轴格式
    # plt.gca().xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
    # plt.gca().xaxis_date()  # 声明X轴使用日期格式
    # plt.xlim(min_time, max_time)  # 显式设置时间范围
    plt.xlabel(f"Time ({min_time.strftime('%Y-%m-%d')})")
    # plt.xscale('log')
    plt.tight_layout()
    plt.savefig(filename)
    logging.info(f"运行时间线已保存至 {filename}")


def get_cpu_info():
    """获取CPU核心信息"""
    process = psutil.Process(os.getpid())
    allowed_cores = process.cpu_affinity()

    # 获取当前运行核心
    current_core = None
    if sys.platform.startswith(('linux', 'darwin')):  # Linux/MacOS
        try:
            current_core = os.sched_getcpu()
        except AttributeError:
            # 对于不支持sched_getcpu的系统，使用psutil降级方案
            current_core = psutil.Process().cpu_num()
    else:  # Windows
        from ctypes import windll
        current_core = windll.kernel32.GetCurrentProcessorNumber()

    # 获取系统总核心数
    total_cores = psutil.cpu_count(logical=True)
    return current_core, [c for c in range(total_cores) if c != current_core]


def worker_loop(core_id, task_queue, task_history):
    """核心工作循环"""
    process = psutil.Process(os.getpid())
    try:
        process.cpu_affinity([core_id])
        logging.info(f"核心 {core_id} 绑定成功")
    except Exception as e:
        logging.error(f"核心 {core_id} 绑定失败: {e}")
        return

    while True:
        try:
            # 从队列获取任务（3秒超时检测）
            index, cmd_args, timeout_args = task_queue.get(block=True, timeout=3)
        except multiprocessing.queues.Empty:
            # 队列持续空置3秒后退出
            break

        # 执行任务
        start_time = datetime.datetime.now()
        # current_core = os.sched_getcpu() if sys.platform.startswith(('linux', 'darwin')) else core_id
        if sys.platform.startswith(('linux', 'darwin')):
            try:
                current_core = os.sched_getcpu()
            except AttributeError:
                current_core = psutil.Process().cpu_num()
        else:
            current_core = core_id
        logging.warning(f"[{current_core}] time:{start_time} 任务 [{index+1}] {cmd_args}   开始")
        try:
            for i, cmd_item in enumerate(cmd_args):
                start_time = datetime.datetime.now()
                timeout=timeout_args[i] if i < len(timeout_args) else None
                # 记录任务元数据
                task_data = {
                    "main_id": index+1,
                    "sub_id": i+1,
                    "core": core_id,
                    "cmd": cmd_item,
                    "timeout": timeout,
                    "start": start_time,
                    "end": datetime.datetime.now()  # 最后更新真实结束时间
                }
                logging.info(f"[{current_core}] {index+1}_{i+1} 命令: {cmd_item}")

                # 使用 Popen 启动子进程，以便后续可以 kill 它
                with subprocess.Popen(
                        cmd_item,
                        stdout=subprocess.DEVNULL,# 防止 I/O 缓冲区阻塞
                        stderr=subprocess.DEVNULL,# 防止 I/O 缓冲区阻塞
                        text=True,
                        start_new_session=True,
                        encoding='utf-8',
                        shell=True
                ) as proc:
                    try:
                        stdout, stderr = proc.communicate(timeout=timeout)
                        end_time = datetime.datetime.now()
                        task_data["end"] = end_time
                        logging.info(f"[{current_core}] time:{end_time} 任务 {cmd_item} 在核心 {core_id} 结束")
                        logging.info(f"任务总耗时: {(end_time - start_time).total_seconds()}")
                    except subprocess.TimeoutExpired:
                        logging.error(f"[{current_core}] [{core_id}]{index + 1}_{i + 1} 超时: {cmd_item}")
                        # proc.kill()  # 直接 kill 子进程
                        # proc.terminate()
                        if sys.platform.startswith('win'):
                            # 使用 Windows 系统命令强制终止进程树
                            subprocess.run(f'TASKKILL /F /T /PID {proc.pid}', shell=True)
                        else:
                            # Unix 系统使用进程组终止
                            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                        stdout, stderr = proc.communicate()  # 等待退出
                        logging.warning(f"已强制终止超时任务[{core_id}]{index + 1}_{i + 1}    {cmd_item}  ")

                task_history.append(task_data)

        except Exception as e:
            logging.error(f"任务执行异常: {e}", exc_info=True)


def create_tasks(command_args, max_core_limit=10):
    current, others = get_cpu_info()
    selected_cores = others[:max_core_limit]

    logging.warning(f"当前核心: {current}/{len(others)+1}")
    logging.warning(f"可用核心池: {selected_cores}")

    """创建核心池执行任务"""
    task_queue = multiprocessing.Queue()
    manager = multiprocessing.Manager()
    task_history = manager.list()

    # 填充任务队列
    for idx, cmd in enumerate(command_args["commands"]):
        if len(cmd["cmd"]) != len(cmd["timeout"]):
            logging.error(f"任务 {idx+1} 命令数量不匹配: {len(cmd['cmd'])} != {len(cmd['timeout'])}")
        task_queue.put((idx, cmd["cmd"], cmd["timeout"]))

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
                filename=f"img_core_pool/task_timeline_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.png")

if __name__ == "__main__":
    if sys.platform.startswith(('linux', 'darwin')):  # Linux/MacOS
        demo_commands = {
            "commands": [
                # {"cmd": [f"python test_tasks.py prime 1000000 5000001", f"python test_tasks.py pi 10000", f"/home/mars/PycharmProjects/python_tests/multi_task/test_task mc 400000000"],"timeout":[None,None,None]},
                # {"cmd": [f"python test_tasks.py pi 10000",  f"/home/mars/PycharmProjects/python_tests/multi_task/test_task fib 48"],"timeout":[None,None]},
                # {"cmd": [f"python test_tasks.py fib 21", f"python test_tasks.py matrix 500",  f"/home/mars/PycharmProjects/python_tests/multi_task/test_task prime 1000000 40000001"],"timeout":[None,None,None]},
                {"cmd": [f"python test_tasks.py mc 50000000"],"timeout":[15]},
                {"cmd": [f"ping baidu.com "], "timeout": [5]},
                {"cmd": [f"python test_tasks.py mc 50000000", f"python test_tasks.py matrix 500000", f"/home/mars/PycharmProjects/python_tests/multi_task/test_task pi 500000"],"timeout":[None,None,None]},
            ]
        }
    else:
        demo_commands = {
            "commands": [
                # {"cmd": [f"c:/python/python310/python.exe test_tasks.py prime 1000000 5000001", f"c:/python/python310/python.exe test_tasks.py pi 10000", f"E:/github/python_tests/multi_task/test_task.exe mc 400000000"],"timeout":[None,None,None]},
                {"cmd": [f"c:/python/python310/python.exe test_tasks.py pi 10000",  f"E:/github/python_tests/multi_task/test_task.exe fib 48"],"timeout":[None,None]},
                {"cmd": [f"c:/python/python310/python.exe test_tasks.py fib 21", f"c:/python/python310/python.exe test_tasks.py matrix 500",  f"E:/github/python_tests/multi_task/test_task.exe prime 1000000 6000001"],"timeout":[None,None,None]},
                {"cmd": [f"c:/python/python310/python.exe test_tasks.py matrix 500"],"timeout":[15]},
                {"cmd": [f"ping baidu.com /t"],"timeout":[5]},
                {"cmd": [f"c:/python/python310/python.exe test_tasks.py mc 1000000", f"c:/python/python310/python.exe test_tasks.py matrix 500", f"E:/github/python_tests/multi_task/test_task.exe pi 5000000000"],"timeout":[None,None,None]},
            ]
        }

    lock_file = os.path.expanduser('~/multi_core_pool.lock')
    lock = portalocker.Lock(lock_file)
    try:
        with lock:
            # 执行任务
            create_tasks(demo_commands, 4)
    except portalocker.exceptions.AlreadyLocked:
        logging.error(f"Another instance of the script is already running.{lock_file}")
        sys.exit(1)
