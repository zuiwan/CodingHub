#!/bin/bash

# CodingLife-测试服
echo "从 Windows-bash 部署-HackGirlfriend-测试服 @Tencent 118.89.27.96"
ssh root@118.89.27.96 '
    cd /root/CodingLife
    echo "-----------强制更新代码-----------"
    git fetch --all
    git reset --hard origin/dev
    echo "-----------重启uwsgi-----------"
    sudo killall -9 -u "www-data" uwsgi
    sudo /root/web2/bin/uwsgi --ini /root/CodingLife/Config/uwsgi.ini &
    echo "-----------重启uwsgi成功，结束-----------"
    exit
'