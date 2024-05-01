import multiprocessing
import time

def worker(num, lock, counter):
    lock.acquire()  # 获取锁
    try:
        print(f"Process {multiprocessing.current_process().name} is working on {num}.")
        time.sleep(1)  # 模拟工作
        with lock:  # 使用上下文管理器再次获取锁
            counter.value += 1  # 访问共享资源
    finally:
        lock.release()  # 释放锁

if __name__ == '__main__':
    shared_counter = multiprocessing.Value('i', 0)  # 共享计数器
    lock = multiprocessing.Lock()  # 创建一个锁
    processes = []

    # 创建多个进程
    for i in range(3):
        p = multiprocessing.Process(target=worker, args=(i, lock, shared_counter))
        processes.append(p)
        p.start()

    # 等待所有进程完成
    for p in processes:
        p.join()

    print(f"Shared counter value: {shared_counter.value}")