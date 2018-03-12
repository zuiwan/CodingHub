FROM ubuntu16.04:latest

#&& apt -y upgrade
RUN apt update \
    && apt -y install mysql-server \
        libmysqlclient-dev  \
        redis-server    \

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5   \
    && echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" \
     | tee /etc/apt/sources.list.d/mongodb-org-3.6.list \
    && apt-get update && apt-get install -y mongodb-org

RUN service mongod start

RUN mkdir -p /root/CodingHub/logs
    && mv /etc/nginx.conf /etc/nginx.conf.bck
    && ln -s /root/CodingHub/Config/nginx.conf /etc/nginx.conf
    && mkdir -p /etc/supervisor/conf.d
    && ln -s /root/CodingHub/Config/supervisord.conf /etc/supervisor/conf.d
RUN apt install