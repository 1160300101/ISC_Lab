import queue
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import psutil
from scapy.all import *
from network.config import opt

raw_data_queue = queue.Queue()
packet_Queue = queue.Queue()
raw_package_queue = queue.Queue()
cond = threading.Condition()
lock = Lock()


def get_netcard():
    result = ''

    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            if item[0] == 2 and "192" in item[1]:
                result = k

    return result


def packet_load(package):
    load = ''
    with cond:
        try:
            proto = package['IP'].proto
            src = package['IP'].src
            dst = package['IP'].dst
            sport = ''
            dport = ''
            if proto == 6:
                load = package['TCP'].payload
                sport = package['TCP'].sport
                dport = package['TCP'].dport
            elif proto == 17:
                load = package['UDP'].payload
                sport = package['UDP'].sport
                dport = package['UDP'].dport

        except IndexError:
            # try:
            #     load = package['IPv6'].payload
            #     # src = package['IPv6'].src
            #     # dst = package['IPv6'].dst
            # except IndexError:
            return

        if len(load) > 0:

            int_ = [int(x) for x in bytes(load)]

            if len(int_) < 1024:
                int_.extend([0] * (1024 - len(int_)))
            else:
                int_ = int_[0:1024]
            img = np.array(int_, dtype='f').reshape((1, 32, 32))
            if img.any():
                amin, amax = img.min(), img.max()
                formed_array = (img - amin) / (amax - amin)
                data = (proto, src, dst, sport, dport, load)

                lock.acquire()
                raw_data_queue.put(formed_array)
                packet_Queue.put(data)
                lock.release()
                cond.notifyAll()


def put_packet(package):
    raw_package_queue.put(package)


def handle_packages():
    with ThreadPoolExecutor(max_workers=opt.num_workers) as executor:
        while not raw_package_queue.empty():
            package = raw_package_queue.get()
            executor.submit(packet_load, package)


def catch_packet(num):
    dev = get_netcard()
    sniff(iface=dev, prn=packet_load, count=num)
