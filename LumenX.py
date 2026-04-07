import json
import re
import requests
import warnings
import threading
import queue
warnings.filterwarnings("ignore")


text = '''\033[31m
   _  __   _____    __  ___           __                                      _  __
  | |/ /  / ___/   /  |/  /          / /   __  __   ____ ___   ___    ____   | |/ /
  |   /   \__ \   / /|_/ /  ______  / /   / / / /  / __ `__ \ / _ \  / __ \  |   /
 /   |   ___/ /  / /  / /  /_____/ / /___/ /_/ /  / / / / / //  __/ / / / / /   |
/_/_|  /____/  /_/  /_/          /_____/\__,_/  /_/ /_/ /_/ \___/ /_/ /_/ /_/|_|
'''
print(text)
print("一款信息收集资产探测工具 version:2.0.0\033[0m\033[32m")
print("[*]BY.林家大少爷")
print("[*]联系方式:L4mTrace")
print("[*]备注:仅内部使用，请勿外传")
#任务流程
#1、把所有 URL 放进队列
#2、开20 个线程
#3、每个线程不断从队列拿任务
#4、处理任务 → 标记完成
#5、队列空了 → 所有线程结束
#6、程序退出
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
}

with open('ip.txt', 'r', encoding='utf-8') as f:
    urls = f.read().splitlines()

task_queue = queue.Queue()#创建任务列表
for url in urls: #把urls放到url里面循坏读取
    task_queue.put(url)  # 把 URL 放入队列put() = 往队列里放任务

print_lock = threading.Lock()  # 创建线程锁防止并发



def scan():
    while not task_queue.empty(): #队列没空就一直干活
        ip = task_queue.get() #从队列拿一个任务出来
        up_ip = ip.replace('http://', '').replace('https://', '').replace('/', '')

        try:
            ips = {'host': ip}
            a = requests.post(url='https://zhanchacha.cn/api/dns/host2ip/', data=ips, headers=header, timeout=5, verify=False)
            x = json.loads(a.text)
            ip_addr = '未知'
            if x.get('data'):
                ip_addr = x['data']['ip']
        except:
            ip_addr = '获取失败'

        try:
            request = requests.get(url=ip, headers=header, timeout=5, verify=False)
            request.encoding = 'utf-8'
            title = re.findall('<title>(.*?)</title>', request.text, re.I)
            title = title[0].replace('&quot;', '').replace('&lrm;;', '').replace('\u03a2ҳ_ǵļ\u0530', '').replace(' -   ֹ    :    ʱ  ܾ   ','').replace('&lrm;','').replace('\u03a2  ҳ_   ǵļ \u0530','').strip() if title else '无标题'
            if request.status_code == 200:
                color_code = "\033[32m"
            elif 400 <= request.status_code <= 600:
                color_code = "\033[31m"
            else:
                color_code = "\033[33m"

            with print_lock:
                print(f'\033[33m 响应码:\033[0m{color_code}[{request.status_code}]\033[0m-->\033[32mIP:{[ip_addr]}\033[0m-->\033[33m 字节长度:{[len(request.text)]}\033[0m-->\033[33m 网站标题:\033[0m\033[34m{[title]}\033[0m-->\033[33murl:\033[0m{request.url}')
                print('-' * 100)
        except:
            pass
        finally:
            task_queue.task_done() #告诉队列：这个任务我处理完了

threads=[]
for i in range(20):#一次开 20 个线程同时跑
    t=threading.Thread(target=scan)#创建一个线程，线程要执行的函数叫 scan
    t.start()
    threads.append(t)

for t in threads:
    t.join()#主线程等着，所有子线程干完再结束

input('[*]探测结束！！！')