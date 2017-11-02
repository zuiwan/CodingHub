#!/bin/bash
echo "-----------进入项目根目录-----------"
cd CodingLife_Server
echo "-----------强制更新Git-----------"
git fetch --all
git reset --hard origin/dev
exit
