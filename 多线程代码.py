import threading
import time

# 1个用法
def worker():
    print("线程开始执行")
    # 模拟耗时任务
    for i in range(5):
        print(f"线程正在工作: {i}")
    print("线程执行完毕")

# 创建线程
thread = threading.Thread(target=worker)
# 启动线程
thread.start()
# 主线程继续执行
print("***主线程继续执行***")

'''传递参数'''
# 2个用法
def worker(name):
    print(f"{name} 线程开始执行")
    for i in range(5):
        print(f"{name} 正在工作: {i}")
        time.sleep(0.5)
    print(f"{name} 线程执行完毕")

thread1 = threading.Thread(target=worker, args=("线程1",))
thread2 = threading.Thread(target=worker, args=("线程2",))
thread1.start()
thread2.start()
# thread1.join()  #等待线程完成
# thread2.join()  #等待线程完成
print("***主线程继续执行***")


def run(t):
    time.sleep(t)
    print(f'我等了{t}秒')
t1 = threading.Thread(target=run, args=(3,))
t2 = threading.Thread(target=run, args=(6,))

t1.start()
print('开始计时')
t2.start()
