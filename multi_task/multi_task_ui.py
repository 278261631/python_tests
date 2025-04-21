import datetime
import json
import multiprocessing
import subprocess

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


def worker_task(core_id, command_args):
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

    # 记录任务开始时间
    start_time = datetime.datetime.now()
    print(f"time:{start_time} 任务 {command_args} 在核心 {current_core} 开始")

    # 启动python 或者其它程序
    result = subprocess.run(
        command_args,
        capture_output=True,
        text=True
    )
    end_time = datetime.datetime.now()
    # 计算任务耗时
    duration = end_time - start_time
    print(f"time:{end_time} 任务 {command_args} 在核心 {current_core} 结束  : {result.stderr}")
    print(f"任务 {command_args} 总耗时: {duration}")


def create_tasks(command_args):
    processes = []
    for j, item_cmd in enumerate(command_args["commands"]):
        print(f"任务 {j} 绑定到核心 {item_cmd['core_id']}")
        item_cmd["core_id"] = selected_cores[i % len(selected_cores)]
        p1 = multiprocessing.Process(
            target=worker_task,
            args=(item_cmd["core_id"], item_cmd["cmd"]),
            name="Core{}_Task".format(item_cmd["core_id"])
        )
        processes.append(p1)

    for p in processes:
        p.start()
        p.join()



if __name__ == "__main__":
    current, others = get_cpu_info()
    max_core_limit = 3
    selected_cores = others[:max_core_limit]
    print(f"当前核心: {current}")
    print(f"其他核心: {others}")
    print(f"已选核心: {selected_cores}")
    # with open('config.json') as f:
    #     config = json.load(f)
    #     commands = config["commands"]
    demo_commands = {
        "commands": [
            {"cmd":f"python test_tasks.py prime 1000000 6000001",},
            {"cmd":f"python test_tasks.py pi 25000",}
        ]
    }

    for i, raw_cmd in enumerate(demo_commands["commands"]):
        raw_cmd["core_id"] = selected_cores[i % len(selected_cores)]

    print(f"demo_commands: {demo_commands}")
    create_tasks(demo_commands)


