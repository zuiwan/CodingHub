#!/bin/bash
echo "激活虚拟环境....."
cd /root/web2 && . bin/activate
echo "-----------进入项目根目录-----------"
cd CodingLife
echo "-----------强制更新Git-----------"
git fetch --all
git reset --hard origin/dev
exit
