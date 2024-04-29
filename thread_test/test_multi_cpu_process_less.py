import multiprocessing
import time

# 创建一个锁
mp_lock = multiprocessing.Lock()


def worker(d_queue, r_queue, p_name):
    while not d_queue.empty():
        try:
            num_item = d_queue.get_nowait()  # 从队列中获取数据
            print(f'queue num  {num_item}')
        except Exception as e:
            break  # 如果队列为空，则结束进程

        # 使用锁来同步对共享资源的访问
        with mp_lock:
            print(f"Process {p_name} is processing data: ")
            time.sleep(3)  # 模拟耗时的工作
            r_queue.put(p_name)  # 将结果放回结果队列
            print(f"Process {p_name} has finished processing data: ")


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
        name = f"Worker_{i+1}"
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
