#!/usr/bin/env bash
cd /root/CodingLife_Server
rm logs/*_supervisor.log

#docker service rm $(docker service ls | awk '{print $1}')

#supervisord
supervisorctl restart uwsgi:CodingLife
#supervisorctl restart celery_cpu
#supervisorctl restart celery_gpu
#supervisorctl restart celery_fork