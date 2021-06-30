## DNS缓存工具
适合DNS服务器不稳定的情况

- [DNS缓存工具](#dns缓存工具)
  - [文件说明](#文件说明)
  - [使用说明](#使用说明)
      - [首次使用](#首次使用)
      - [日常使用](#日常使用)
      - [其他功能](#其他功能)

### 文件说明
- `dns.vbs`
  将系统的dns缓存添加到hosts文件中
- `hosts.vbs`
  更新hosts文件中hostname对应的ip
- `dns.txt`
  第一行填入包含dns服务器地址的文件路径（`randomdns`工具的dns.txt）
- `skip.txt`
  在hosts文件中不需要更新的域名

### 使用说明
##### 首次使用
将dns.vbs配置到Windows计划任务，每分钟执行一次。执行一天，将大部分需要访问的网站dns缓存转换为hosts文件内容

##### 日常使用
1. 将dns.vbs定时时间间隔调整为一个较长的时间间隔，例如5分钟
2. 将hosts.vbs配置到window计划任务中，设置一个较长的时间间隔，例如6小时。

##### 其他功能
需要在具有管理员权限的命令行中执行，否则无法看到输出内容
1. 查询域名对应的ip
    `python dnscache.py lookup you_host_name`
2. 将单个域名的ip更新到hosts文件中
   `python dnscache.py update you_host_name`