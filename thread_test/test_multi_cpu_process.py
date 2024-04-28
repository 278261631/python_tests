# import multiprocessing
# import time
#
# import numpy as np
#
# max_process = 3
#
#
# def worker(num, lock, counter):
#     lock.acquire()  # 获取锁
#     try:
#         print(f"Process {multiprocessing.current_process().name} is working on {num}.")
#         time.sleep(3)  # 模拟工作
#         with lock:  # 使用上下文管理器再次获取锁
#             counter.value += 1  # 访问共享资源
#     finally:
#         lock.release()  # 释放锁
#
#
# if __name__ == '__main__':
#     shared_counter = multiprocessing.Value('i', 0)  # 共享计数器
#     mp_lock = multiprocessing.Lock()  # 创建一个锁
#     processes = []
#     arr = np.arange(1, 11)  # 示例数组
#     n_parts = 3  # 想要分割的份数
#
#     # 进行分割
#     parts = np.array_split(arr, n_parts)
#     print(len(parts))
#
#
#     # 创建多个进程
#     for i in range(max_process):
#         p = multiprocessing.Process(target=worker, args=(i, mp_lock, shared_counter))
#         processes.append(p)
#         p.start()
#
#     # 等待所有进程完成
#     for p in processes:
#         p.join()
#
#     print(f"Shared counter value: {shared_counter.value}")


import multiprocessing
import time

# 创建一个锁
mp_lock = multiprocessing.Lock()


def worker(data_queue, results_queue, name):
    while not data_queue.empty():
        try:
            num = data_queue.get_nowait()  # 从队列中获取数据
        except Exception as e:
            break  # 如果队列为空，则结束进程

        # 使用锁来同步对共享资源的访问
        with mp_lock:
            print(f"Process {name} is processing data: {num}")
            time.sleep(1)  # 模拟耗时的工作
            results_queue.put(num)  # 将结果放回结果队列
            print(f"Process {name} has finished processing data: {num}")


if __name__ == '__main__':
    # 假设这是你的数据列表
    data = list(range(1, 6))

    # 创建数据队列和结果队列
    data_queue = multiprocessing.Queue()
    results_queue = multiprocessing.Queue()

    # 将数据放入数据队列
    for num in data:
        data_queue.put(num)

    # 定义同时运行的最大进程数
    MAX_CONCURRENT_PROCESSES = 2

    # 创建进程列表
    processes = []

    # 启动进程
    for i in range(MAX_CONCURRENT_PROCESSES):
        name = f"Worker-{i+1}"
        proc = multiprocessing.Process(target=worker, args=(data_queue, results_queue, name))
        processes.append(proc)
        proc.start()

    # 等待所有进程完成
    for proc in processes:
        proc.join()

    # 打印结果
    while not results_queue.empty():
        print(f"Result: {results_queue.get()}")

    print("All tasks have been completed.")
