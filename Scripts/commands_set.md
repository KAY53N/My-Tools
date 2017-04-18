
### 查看文件排除以#或;开始的行或空白行，适合查看配置文件
    egrep -v "^#|^$" php.ini | sed '/[#|;].*$/d; /^ *$/d'

### 删除空格和空行
    sed '/^$/d' filename
    sed 's/ //g' filename
    sed 's/[[:space:]]//g' filename

### 以内存大小排序列出进程
    ps aux --sort=rss |sort -k 6 -rn

### 以管道输入方式修改用户密码
    echo "password" |passwd –stdin root

### 通过SSH快速备份文件到另一服务器
    tar zcvf - back/ | ssh root@www.jb51.net tar xzf - -C /root/back/

### 生成随机字符
    cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1

