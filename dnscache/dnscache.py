import ctypes
import datetime
import json
import logging
import logging.config
import os
import sys
import time
import traceback
from pathlib import Path
from random import shuffle
from shutil import copyfile
from typing import List

from appdirs import AppDirs
from nslookup import Nslookup
from python_hosts import Hosts, HostsEntry


def update_from_dns_cache():

    logger = logging.getLogger('dns')
        
    time.sleep(5)
    hosts = Hosts()
    dns_cache = DnsCache()
    dns_cache.load_entries_from_cache()
    logger.info('find ' + str(len(dns_cache.entries)) + ' records')
    hosts.add(entries=dns_cache.entries, force=True)
    hosts.write()


def update_hosts_file():

    logger = logging.getLogger('hosts')
    data_dir = getAppDirs().user_data_dir
    hosts_path = Hosts.determine_hosts_path()
    backup_hosts_name = 'hosts.' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_hosts_path = str(Path(data_dir) / Path(backup_hosts_name))
    copyfile(hosts_path, backup_hosts_path)
    logger.info('backup hosts to ' + backup_hosts_path)

    discard_hostname_file_path = str(Path(data_dir) / Path('discardhosts.txt'))
    last_discard_hostnames = read_config_as_list(discard_hostname_file_path)
    discard_hostnames:List[str] = list()

    # 加载查询使用的dns服务器
    dns_servers = list()
    dns_config_file_path = Path('./dns.txt', encoding='utf-8').read_text().strip()
    dns_servers = read_config_as_list(dns_config_file_path)
    dns_servers = list(dict.fromkeys(dns_servers))
    skip_hostnames = read_config_as_list('skip.txt')
    # 查询IP地址，并更新hosts文件
    hosts = Hosts()
    known_hosts = set()

    #先查询上一次查询失败的hostname
    logger.info('search discard hostnames')
    to_be_add_entries:List[HostsEntry] = list()
    for discard_hostname in last_discard_hostnames:
        entries:List[HostsEntry] = query_entries_by_hostname(discard_hostname, dns_servers, known_hosts)
        if len(entries) == 0:
            logger.debug('can not find ip, remove hostname: ' + discard_hostname )
            hosts.remove_all_matching(name=discard_hostname)
            discard_hostnames.append(discard_hostname)
            continue
        to_be_add_entries += entries
        logger.debug('add host ' + discard_hostname + ':' + str([e.address for e in entries]) + 'to cache')

    # 更新hosts文件中的ip
    for e in hosts.entries:
        entry: HostsEntry = e   
        if entry.entry_type != 'ipv4':
            continue    
        for name in entry.names:
            if name in skip_hostnames:
                logger.debug('skip host ' + name + ': user config')
                continue
            if name in known_hosts:
                logger.debug('skip host ' + name + ': known host')
                continue
            try:
                # 每次随机排序dns服务器
                shuffle(dns_servers)
                entries:List[HostsEntry] = query_entries_by_hostname(name, dns_servers, known_hosts)
                if len(entries) == 0:
                    logger.info('can not find ip,  hostname: ' + name )
                    discard_hostnames.append(name)
                    continue
                #hosts.add(entries, force=True, allow_address_duplication=True, merge_names=True)
                to_be_add_entries += entries
                logger.debug('update host ' + name + ' old: ' + entry.address + ' new:' + str([e.address for e in entries]) + ' to cache')
            except:
                logger.info('exception occured, remove hostname: ' + name )
                discard_hostnames.append(name)
                logger.info(traceback.format_exc())
    logger.info('add ' + str(len(to_be_add_entries)) + ' entries to hosts')
    hosts.add(to_be_add_entries, force=True, allow_address_duplication=True, merge_names=True)
    if not is_admin():
        get_admin()
    time.sleep(5)
    logger.info('discard hostname :' + str(len(discard_hostnames)))
    write_config_from_list(discard_hostname_file_path, discard_hostnames)
    logger.info('write discard hostname done')
    hosts.write()
    logger.info('write hosts file done')


def lookup_hostname(hostname):
    logger = logging.getLogger('lookup')
    dns_servers = list()
    dns_config_file_path = Path('./dns.txt', encoding='utf-8').read_text().strip()
    dns_servers = read_config_as_list(dns_config_file_path)
    dns_servers = list(dict.fromkeys(dns_servers))
    entries:List[HostsEntry] = query_entries_by_hostname(hostname, dns_servers)
    if len(entries) == 0:
        logger.info('hostname not found')
        return []
    logger.info('find ip: ' + str([e.address for e in entries]))
    hosts = Hosts()
    entries_in_hosts = hosts.find_all_matching(name=hostname)
    logger.info('ip in hosts: ' + str([e.address for e in entries]))
    os.system('pause')
    return entries


def update_hostname(hostname):
    logger = logging.getLogger('update')
    entries = lookup_hostname(hostname)
    if len(entries) > 0:
        hosts = Hosts()
        hosts.add(entries, force=True, allow_address_duplication=True, merge_names=True)
        hosts.write()
    os.system('pause')


def query_entries_by_hostname(name, dns_servers, known_hosts=set()) -> List[HostsEntry]:
    dns_query = Nslookup(dns_servers=dns_servers)
    ips_record = dns_query.dns_lookup(name)
    entries:List[HostsEntry] = list()
    for address in ips_record.answer:
        he = HostsEntry(entry_type='ipv4', address=address, names=[name])
        entries.append(he)
        known_hosts.add(name)
    return entries  


def read_config_as_list(file_path) -> List[str]:
    if not os.path.exists(file_path):
        return []
    config_data:List[str] = list()
    for line in open(file_path, encoding='utf-8'):
        if line.startswith('#'):
            continue
        line = line.strip()
        if len(line) > 0:
            config_data.append(line.strip())
    return config_data


def write_config_from_list(file_path, lines:List):
    with open(file_path, 'w', newline=os.linesep) as f:
        for line in lines:
            f.write(line + '\n')


class DnsCache:

    dns_cache_record_begin = '----------------------------------------'
    dns_cache_record_name = '记录名称'
    dns_cache_a_record = 'A (主机)记录'

    def __init__(self):
        self.entries:List[HostsEntry] = list()
    
    def load_entries_from_cache(self):
        self.entries.clear()
        r = os.popen('ipconfig /displaydns')
        result = r.read()
        r.close()
        lines = result.splitlines()
        line_cnt = len(lines)
        i = 0
        while i < line_cnt:

            text = lines[i].strip()

            if len(text) == 0:
                i = i + 1
                continue

            if not self.dns_cache_record_begin in text:
                i = i + 1
                continue

            # 找到开始标记
            lineno_record_name = i + 1
            lineno_a_record = i + 6
            # 剩余行数不够，结束
            if lineno_a_record >= line_cnt:
                i = line_cnt
                continue
            record_name_line = lines[lineno_record_name]
            a_record = lines[lineno_a_record]
            # 检查指定行是否包含特定标记
            if not (self.dns_cache_record_name in lines[lineno_record_name] and self.dns_cache_a_record in lines[lineno_a_record]):
                i = i + 7
                continue
            arr_record_name = record_name_line.split(':')
            arr_a_record = a_record.split(':')
            if len(arr_record_name) != 2 or len(arr_a_record) != 2:
                i = i + 7
                continue
            record_name = arr_record_name[1].strip()
            a_record = arr_a_record[1].strip()
            entry = HostsEntry('ipv4', address=a_record, names=[record_name])
            self.entries.append(entry)
            i = i + 7


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_admin():
    if sys.version_info[0] == 3:
    	ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:#in python2.x
        ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1)


def getAppDirs():
    return AppDirs("DNSCache", "MyPythonTools")


if __name__ == '__main__':

    log_config = './logging.json'

    print('working dir', os.getcwd())
    print('program dir', os.path.dirname(__file__))
    print(str(Path(log_config).absolute()))

    dirs = getAppDirs()

    if not os.path.exists(dirs.user_log_dir):
        os.makedirs(dirs.user_log_dir)
    if not os.path.exists(dirs.user_data_dir):
        os.makedirs(dirs.user_data_dir)
    print('log dir: ', dirs.user_log_dir)
    print('data dir: ', dirs.user_data_dir)
    log_file = (Path(dirs.user_log_dir) / (sys.argv[1] + '.txt')).absolute()
    print('log file: ', log_file)
    log = logging.getLogger('root')
    try:
        log_config_text = Path(log_config).read_text(encoding='utf-8-sig')
        log_config_text = log_config_text.replace('{log_file}', str(log_file).replace('\\', '/') )
        logging.config.dictConfig(json.loads(log_config_text))
    except Exception:
        log.critical('Exception content: \n{}'.format(traceback.format_exc()))
    if is_admin():
        try:
            if sys.argv[1] == 'dns':
                update_from_dns_cache()
            elif sys.argv[1] == 'hosts':
                update_hosts_file()
            elif sys.argv[1] == 'lookup':
                lookup_hostname(sys.argv[2])
            elif sys.argv[1] == 'update':
                update_hostname(sys.argv[2])
        except:
            log.critical('Exception content: \n{}'.format(traceback.format_exc()))
        finally:
            sys.exit(0)
    else:
        get_admin()
