import ctypes, sys, logging, os, logging.config, json, traceback
from pathlib import Path, PureWindowsPath
from random import shuffle
#import win32process
import wmi
from appdirs import AppDirs



def main():

    dirs = AppDirs("RandomDNS", "MyPythonTools")

    if not os.path.exists(dirs.user_log_dir):
        os.makedirs(dirs.user_log_dir)
    print('log dir: ', dirs.user_log_dir)

    log_config = './logging.json'
    log_file = (Path(dirs.user_log_dir) / 'log.txt').absolute()
    print('log file: ', log_file)
    log = logging.getLogger('root')
    try:
        log_config_text = Path(log_config).read_text(encoding='utf-8-sig')
        log_config_text = log_config_text.replace('{log_file}', str(log_file).replace('\\', '/') )
        logging.config.dictConfig(json.loads(log_config_text))
    except Exception:
        log.critical('Exception content: \n{}'.format(traceback.format_exc()))

    logger = logging.getLogger('dns')

    dns_servers = list()
    for line in open('./dns.txt', encoding='utf-8'):
        if line.startswith('#'):
            continue
        line = line.strip()
        if len(line) > 0:
            dns_servers.append(line.strip())

    dns_servers = list(dict.fromkeys(dns_servers))
    logger.info('dns servers:')
    logger.info(dns_servers)
    logger.info('shuffle dns servers')
    shuffle(dns_servers)
    logger.info('dns servers:')
    logger.info(dns_servers)
    if not is_admin():
        logger.info('need admin')
        get_admin()
    wmi_server = wmi.WMI()
    network_configs = wmi_server.Win32_NetworkAdapterConfiguration(IPEnabled=True)
    for config in network_configs:
        result = config.SetDNSServerSearchOrder(DNSServerSearchOrder=dns_servers)
        logger.info('set')
        logger.info(config)
        logger.info('result: ')
        logger.info(result)

    #hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    #if hwnd != 0:
    #    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    #    os.system('taskkill /PID ' + str(pid) + ' /f')
    sys.exit()
    

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_admin():
    if sys.version_info[0] == 3:
    	ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    else:#in python2.x
        ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1)



if __name__ == '__main__':
    main()
