import requests
import time
import os
import ntplib
import datetime
import urllib.request
import sys
from bs4 import BeautifulSoup
import dateparser
import logging
import appdirs
from appdirs import AppDirs


def main():

    dirs = AppDirs("SyncTime", "MyPythonTools")

    if not os.path.exists(dirs.user_log_dir):
        os.makedirs(dirs.user_log_dir)
    
    logging.getLogger().setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")

    handler = logging.FileHandler(os.path.join(dirs.user_log_dir, 'log.txt'), mode='a')
    handler.setLevel(logging.DEBUG)
    
    handler.setFormatter(formatter)
    
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)

    logging.getLogger().addHandler(handler)
    logging.getLogger().addHandler(console)


    wait_count = 0

    logging.info('开始检测网络...')
    while True:

        if is_connected():
            logging.info('网络连通')
            break

        else:
            wait_count = wait_count + 1
            logging.info('网络连接失败' + str(wait_count))
            time.sleep(1)

            if wait_count > 20:
                logging.info('没有网络连接，退出')
                sys.exit()
    

    ntp_servers = get_ntp_server_list()

    for ntp_server in ntp_servers:
        if get_time_from_ntp(ntp_server):
            return

    # +8时区
    if time.localtime().tm_gmtoff == 28800:
        if get_time_from_www_shijian_com():
            return
        
        
        if get_time_from_time_tianqi_com():
            return


        if get_time_from_www_beijing_time_org():
            return


        if get_time_from_biaozhunshijian_51240_com():
            return


def  is_connected():
    try:
      requests.get("http://www.baidu.com", timeout=2)
    except:
        return False
    return True


def get_time_from_ntp(ntp_server_addr):
    logging.info('尝试：' + ntp_server_addr)
    try:
        c = ntplib.NTPClient()
        response = c.request(ntp_server_addr)
        ts = response.tx_time
        update_system_date_time(time.localtime(ts))
        return True
    except Exception as e:
        logging.info(e)
        return False


def get_time_from_www_shijian_com():
    try:
        url = 'http://www.shijian.cc/000/clock.asp'
        logging.info(url)
        content = get_text_content(url)
        date_time_str = content.replace('/','-').replace('/', '-')
        date_time = dateparser.parse(date_time_str)
        update_system_date_time(date_time.timetuple())
        return True
    except Exception as e:
        logging.debug(e)
        return False


def get_time_from_www_beijing_time_org():
    try:
        url = 'http://www.beijing-time.com/'
        logging.info(url)
        content = get_text_content(url)
        soup = BeautifulSoup(content, features="lxml")
        times = soup.select("#bjtime")
        date_time_str = times[0].get_text()
        date_time = dateparser.parse(date_time_str)
        update_system_date_time(date_time.timetuple())
        return True
    except Exception as e:
        print(e)
        return False
    pass

def get_time_from_time_tianqi_com():
    url = 'http://time.tianqi.com/'
    logging.info(url)
    content = get_text_content(url)
    soup = BeautifulSoup(content, features="lxml")
    times = soup.select("#times")
    date_time_str = times[0].get_text()
    date_time = dateparser.parse(date_time_str)
    update_system_date_time(date_time.timetuple())


def get_time_from_biaozhunshijian_51240_com():
    try:
        url = 'https://biaozhunshijian.51240.com/web_system/51240_com_www/system/file/biaozhunshijian/time/?v=' + str(int(time.time()*1000))
        logging.info(url)
        content = get_text_content(url)
        start = content.find(':') + 1
        end = content.find('}')
        millions = float(content[start:end])/1000
        update_system_date_time(time.localtime(millions))
        return True
    except Exception as e:
        logging.info(e)
        return False

def get_text_content(url):
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3775.400 QQBrowser/10.6.4208.400',
        'Connection':'keep-alive',}
    res = None
    try:
        req = urllib.request.Request(url,headers=headers)
        res = urllib.request.urlopen(req)
        content = res.read().decode('utf8')
        return content
    except Exception as e:
        raise e
    finally:
        if req:
            res.close()

def update_system_date_time(time_tuple):

    commands = None

    if sys.platform == 'linux2' or sys.platform == 'linux':
        commands = _linux_set_time(time_tuple)

    elif sys.platform == 'win32':
        commands = _win_set_time(time_tuple)
    
    else:
        raise Exception('不支持的操作系统')

    for cmd in commands:
        logging.info('执行：' + cmd)
    
    logging.info('时间更新命令执行成功')


def get_ntp_server_list(load_default_on_error=True):
    ntp_servers = []
    try:
        for line in open('nptservers.txt'):
            ntp_servers.append(line.strip())
    except:
        logging.info('加载ntpservers.txt失败')
        if load_default_on_error:
            ntp_servers = ['time.ustc.edu.cn', 'ntp.sjtu.edu.cn', 'ntp.fudan.edu.cn',
                           'ntp.neu.edu.cn', 'ntp.shu.edu.cn', 'ntp.nju.edu.cn',
                           'cn.ntp.org.cn', 'cn.pool.ntp.org', 'asia.pool.ntp.org', 'edu.ntp.org.cn',
                           'time.buptnet.edu.cn', 'ntp.aliyun.com', 'time.asia.apple.com',
                           'time.windows.com', 'ntp.ntsc.ac.cn', 'stdtime.gov.hk',
                           'time.smg.gov.mo', 'time.kriss.re.kr', 'ntp.nict.jp',
                           's2csntp.miz.nao.ac.jp', 'time.nist.gov', 'uk.pool.ntp.org', 'de.pool.ntp.org',
                           'fr.pool.ntp.org', 'es.pool.ntp.org', 'it.pool.ntp.org', 'nl.pool.ntp.org',
                           'no.pool.ntp.org', 'pt.pool.ntp.org', 'se.pool.ntp.org',]
    return ntp_servers

def _win_set_time(time_tuple):
    date_str = time.strftime("%Y-%m-%d", time_tuple)
    time_str = time.strftime("%H:%M:%S", time_tuple)
    cmd_str = 'date {} && time {}'.format(date_str, time_str)
    os.system(cmd_str)
    return [cmd_str, ]


def _linux_set_time(time_tuple):
    import subprocess
    import shlex
    from _datetime import datetime

    time_string = datetime(*time_tuple).isoformat()
    # os.system('date -s "' + time_string + '"')
    cmd_list = ["timedatectl set-ntp false", # May be necessary
                "sudo date -s '%s'" % time_string, 
                "sudo hwclock -w" ]
    
    for cmd in cmd_list:
        subprocess.call(shlex.split(cmd))

    return cmd_list


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.info(e)
        raise e

