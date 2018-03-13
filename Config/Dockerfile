FROM ubuntu16.04:latest

#&& apt -y upgrade
RUN apt update \
    && apt -y install mysql-server \
        libmysqlclient-dev  \
        redis-server    \
        python-pip  \

ENV LC_ALL=C
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5   \
    && echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" \
     | tee /etc/apt/sources.list.d/mongodb-org-3.6.list \
    && apt-get update && apt-get install -y mongodb-org

RUN service mongod start

RUN mkdir -p /root/CodingHub/logs
    && mkdir -p /var/log/supervisor/
    && mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bck
    && ln -s /root/CodingHub/Config/nginx.conf /etc/nginx/nginx.conf
    && mkdir -p /etc/supervisor/conf.d
    && ln -s /root/CodingHub/Config/supervisord.conf /etc/supervisor/
    && ln -s /root/CodingHub/Config/nginx_uwsgi.conf /etc/nginx/conf.d/
RUN mysql -uroot -proot -e"CREATE DATABASE zuiwan; CREATE USER 'zuiwan'@'%' IDENTIFIED BY 'zuiwan2018'; GRANT ALL ON *.* TO
 'zuiwan'@'%';"

RUN supervisor