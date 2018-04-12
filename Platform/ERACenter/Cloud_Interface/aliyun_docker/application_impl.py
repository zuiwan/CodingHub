#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     application_impl
   Description :
   Author :       huangzhen
   date：          2018/1/2
-------------------------------------------------
   Change Activity:
                   2018/1/2:
                   2018/02/26: split run.sh as 3 parts
-------------------------------------------------
"""

__author__ = 'huangzhen'
import time
import os
import stat
from functools import wraps
import json
import datetime
import traceback

from Platform.ConfCenter.redis_config_store import (
    machine_resource_limit,
    MACHINE_RESOURCE_QUEUE_REDIS_KEY_PREFIX,
    MACHINE_SCALING_FLAG_REDIS_KEY,
)
from Library.Utils import time_util as date_utils, file_util
from Library.Utils.file_util import get_dir_total_size
from constants import (
    GPU_INSTANCE_TYPE,
    CPU_INSTANCE_TYPE,
    SERVER_CONFIG_MAP,
    TASK_ARREARS_LOG,
    TASK_ARREARS_LOG,
    INFLUXDB_INTERFACE
)
from Platform.ConfCenter.manager import Configurator
from Library.extensions import orm as db, rdb
from Platform.ConfCenter.constants import (
    DOCKER_PRE,
    DOCKER_IMAGE_CONFIG,
    PLAN_PRICE_CONFIG,
    PACKAGE_PRICE_CONFIG,
    BILL_CONFIG
)
from utils import Write_Job_Log, Get_Code_Module, Influxdb_Controler
from Library.Utils.time_util import string_toDatetime
from application import Application_Center
from cluster import Cluster
from setting import (
    FIX_PERMISSIONS_IN_CONTAINER,
    JUPYTER_CSS,
    IFRAME_CUSTOM_JS
)
from Platform.ERACenter.Cloud_Interface.aliyun_docker.constants import CLUSTER_ID_MAP
from Library.Utils.log_util import LogCenter

Configurator_Ist = Configurator.instance()
impl_logger = LogCenter.instance().get_logger("aliyun_docker", "applicationImpl")

FAIL_RETRY_MAX_CNT = 3  # 最大重试次数
FAIL_RETRY_INTERVAL = 5  # 重试最小间隔
INIT_SLEEP_TIME = 3  # 开始轮询为3s
RUNNING_SLEEP_TIME = 10  # 在任务进入运行状态后，轮询间隔改为10s


def active_dbmodel(models=()):
    '''
    Application类的db_model补丁，确保实例所持有的db.model类型的属性是绑定在数据库会话上的
    依赖于 Applicaiton类中@property 所装饰的几个函数（实际的绑定会话执行者）
    '''

    def decorate(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                [args[0].__setattr__(model, args[0].__getattribute__(model + "_model"))
                 for model in models if hasattr(args[0], model)]
                res = f(*args, **kwargs)
            except Exception as e:
                raise e
            return res

        return wrapper

    return decorate


from .utils import Get_User, Get_Job
from Library.extensions import orm as db


class Application(Application_Center):
    '''
    实现experiment/run整个流程的类。
    1. 继承自Application_Center类，继承了阿里云http接口的方法
    2. __init__函数执行了最简的任务初始化操作
    3. Run()函数
    4. 调用Run()之后必须调用Do_Before_Remove()执行清理操作（可以考虑做成上下文管理器，自动清理）
    '''
    WORKING_DIR = "/workspace"
    CUSTOM_JS_FORMAT = "define(['base/js/namespace'], function (Jupyter) {{ {js_code} }})"
    SINGLE_TAG_JS = "Jupyter._target = '_self';"
    COMMON_SH_HEADER = "#!/bin/sh\n# Copyright © RussellCloud 2017"
    SET_DEFAULT_TERMINAL_DIR = '''if [ -d {working_dir} ];then\ncd {working_dir}\nfi'''
    TERMINAL_SYMBOL_RAW = "##### END OF FILE - ID : {} #####"

    def __init__(self, job_id, time_limit=0, run_as_root=True):
        self.job_id = job_id
        self.job = Get_Job(id=job_id)
        self.user = Get_User(id=self.job.uid)
        self.time_limit = time_limit
        self.workdir = os.path.join("/root/workspace", job_id)
        self.is_test_env = True
        self.is_run_as_root = run_as_root
        self.db = db
        self.app_name = self.job.app_name
        self.cluster_ist = Cluster(cluster_id=CLUSTER_ID_MAP.get(self.job.machine_type))
        self.retry_cnt = 0  # 重试次数
        super(Application, self).__init__(cluster=self.cluster_ist.cluster_info)

    def Run(self):
        '''
        建造者模式
        :return:
        '''
        ok = self.Init_Task()
        if not ok:
            return ok
        ok = self.Init_Aliyun()
        if not ok:
            return ok
        ok = self.Create_App()
        if not ok:
            return ok
        ok = self.Polling_State()
        if not ok:
            return ok
        ok = self.Do_Before_Remove()
        if not ok:
            return ok
        return True

    @property
    def experiment_model(self):
        return self.db.session.merge(self.job)

    @property
    def user_model(self):
        return self.db.session.merge(self.user)

    @active_dbmodel(("experiment"))
    def Create_App(self):
        self.Write_Log("Pulling image from remote, maybe take a while...")
        application_result = False
        while not application_result:
            application_result, application_content = self.app_create(self.app_name, template=self.content)
            if application_result:
                self.Write_Log("Task create successfully", "VERBOSE")
                break
            else:
                # No volume work-app_name on node cluster_id-nodexx (error: Key not found in store). Please recreate the volume
                impl_logger.debug(
                    "application_result={}, application_content={}".format(application_result, application_content))
                if "error: Key not found in store" in application_content:  # 新扩容的机器状态未准备好,重新创建
                    self.volume_create(self.work_name, "nas", self.work_nfs_opts)
                    time.sleep(1)  # 避免段时间内触发大量创建请求

                else:
                    self.Write_Log("Task create failed, " + application_content, "ERROR")
                    return False
        try:
            current_state, created, updated = self.get_application_info(self.app_name)
            self.datetime_to_stop = string_toDatetime(created) + datetime.timedelta(seconds=self.time_limit or 0)
        except Exception as e:
            self.Write_Log(str(e), "VERBOSE")
            self.datetime_to_stop = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.time_limit or 0)
        return True

    def Check_Has_Resource(self):
        # 获取当前集群的机器数量和服务数量
        machine_size = self.cluster_ist.info(self.cluster_ist.cluster_id)['size']
        service_list = self.service_list()
        # 统计服务数量
        service_name = "user-application"
        service_num = 0
        for service in json.loads(service_list[1]):
            if service_name in service['name']:  # 覆盖测试和正式环境的服务
                service_num += 1
        machine_task_limit = machine_resource_limit.get(self.job.instance_type)[
            "concurrency"]  # cpu=2 即cpu集群每台最多运行两个任务
        has_resource = (machine_size * machine_task_limit) > service_num
        if not has_resource:
            impl_logger.debug("lack of resource, machine_num={},service_num={}".format(machine_size, service_num))
        return has_resource

    def Check_Is_Scaling(self):
        # 检测集群状态来判断是否在扩容中
        cluster_info = self.cluster_ist.info(self.cluster_ist.cluster_id)
        return cluster_info["state"] == "scaling"

    def Ensure_Cluster_Resource(self, poll_interval=3):
        """
        堵塞确保集群有充足的资源
        :param poll_interval:轮询间歇
        :return: 出现异常情况返回False,有资源返回True
        """
        is_tip = False
        try_cnt = 0
        # TODO 考虑多进程并发操作资源冲突的情况，如两任务同时触发机器扩容
        while not self.Check_Has_Resource():  # 轮询直到有资源
            if not is_tip:
                is_tip = True
                self.Write_Log(
                    "Lack of machine resource. The cluster is scaling. It will take more time than normal...")
            if not self.Check_Is_Scaling():  # 没有扩容，则进行扩容
                try:
                    cluster_type = "cpu" if self.job.instance_type == CPU_INSTANCE_TYPE else "gpu"
                    # ret = {"code":"200","message":"","requestId":"9a7ee3fd-7be1-4adb-9bca-1cf2c8642391"}
                    if try_cnt >= 3:  # 单个任务伸缩情况超过3次，暂判定集群伸缩异常，如账户余额不够、弹性ip不够等
                        return False

                    try_cnt += 1
                    ret = self.cluster_ist.triggle_scale_out(self.cluster_ist.cluster_id, cluster_type=cluster_type)
                    result = json.loads(ret)
                    if result["code"] != "200":  # 扩容失败
                        raise Exception("scale api request failed:{}".format(ret))
                    impl_logger.info("trigger_scale_out executed, result:{}".format(result))
                    time.sleep(poll_interval)  # 防止阿里云状态延迟
                except Exception as e:
                    impl_logger.error("scale out failed, reason:{}".format(str(e)))
                    return False
            time.sleep(poll_interval)
        return True

    def Write_Log(self, msg, level="INFO"):
        Write_Job_Log(self.job_id, msg, level)

    def append_terminal_symbol(self, file_path="/root/workspace/log", file_name="container.log"):
        try:
            with open(os.path.join(file_path, self.job_id, file_name), 'a') as f:
                f.write(self.TERMINAL_SYMBOL_RAW.format(self.job_id))
        except Exception as e:
            self.Write_Log("Append terminal symbol failed. The reason is %s" % str(e))

    @active_dbmodel(("experiment", "instance", "user"))
    def Do_Before_Remove(self):
        '''
        :return:
        '''

        # 添加终结符
        self.append_terminal_symbol()

        if self.job.state == "waiting":
            self.job.state = "failed"
            self.db.session.commit()
            self.Write_Log("Task schedule failed...", "ERROR")
            return True

        current_state, created, updated = self.get_application_info(self.app_name)

        if current_state not in ["stopped", "finished"]:
            # if Is_Test_Server():
            #     impl_logger.debug("try sleep some time to catch fail detail")
            #     time.sleep(60)
            stop_result, stop_content = self.app_stop(self.app_name)
            if stop_result:
                self.Write_Log("Task has been stopped")
                current_state, created, updated = self.get_application_info(self.app_name)
            else:
                self.Write_Log("Task stop failed, reason: %s" % stop_content, "ERROR")
        if not self.job.started:
            # in case started not set
            self.job.started = string_toDatetime(created)
        self.job.ended = string_toDatetime(updated)
        self.job.duration = int((self.job.ended.replace(tzinfo=None) - self.job.started.replace(
            tzinfo=None)).total_seconds())
        self.db.session.commit()

        del_result, del_content = self.app_delete(self.app_name, volume="true")
        if not del_result:
            self.Write_Log("Task del failed, reason: %s" % del_content)

        # make sure app delete done
        retry_time = 5
        while retry_time > 0:
            retry_time -= 1
            info_result, info_content = self.app_info(self.app_name)
            if not info_result:
                self.Write_Log("Task %s del success." % self.app_name)
                break
            time.sleep(4)
        # self.Write_Job_Log("Volume deleting")

        if self.data_name:
            for index in range(len(self.job.data_id_list)):
                v_del_result, v_del_content = self.volume_delete(self.data_name.replace("##INDEX##", str(index)))
                if not v_del_result:
                    self.Write_Log("data volume del failed, reason: %s" % v_del_content)

        w_del_result, w_del_content = self.volume_delete(self.work_name)
        if not w_del_result:
            self.Write_Log("work volume del failed, reason: %s" % w_del_content)

        self.Write_Log("[{}] Finishing execution in {} seconds for Task".format(current_state,
                                                                                self.job.duration))

        self.job.output_size = get_dir_total_size(os.path.join(self.workdir, "output"),
                                                  unit="MB")
        self.db.session.commit()

        ###### 结账 #####
        if not self.Pay_Bill():
            self.Write_Log("任务扣费失败", "VERBOSE")
            return False

        return True

    @active_dbmodel(("experiment", "instance", "user"))
    def Polling_State(self):
        '''
        :return:
        '''
        retry_times = 0
        start_running_ok = False
        sleep_time = INIT_SLEEP_TIME
        while True:
            try:
                # current_state = _application.get_application_status(name)
                current_state, created, updated = self.get_application_info(self.app_name)
                if date_utils.get_datetime_utcnow() >= self.datetime_to_stop.replace(tzinfo=None):
                    self.Write_Log("maximum length of running-time reached", "ERROR")
                    self.job.state = "timeout"
                    self.db.session.commit()
                    break
            except Exception, e:
                self.Write_Log("Task status refresh failed: {}, retrying...".format(str(e)), "WARNING")

                retry_times += 1
                if retry_times >= 10:
                    self.Write_Log("Task retry too much times, closed!", 'WARNING')
                    self.job.state = "failed"
                    self.db.session.commit()
                    # Do_Before_Remove()
                    break
            else:
                if self.job.state == "stopped":
                    if rdb.sismember(TASK_ARREARS_LOG, self.job.id):
                        rdb.srem(TASK_ARREARS_LOG, self.job.id)
                    else:
                        self.Write_Log('#' * 20)
                    self.Write_Log("Task shutdown...")
                    # self.Do_Before_Remove()
                    # _application.app_kill(name)
                    break
                if not current_state:
                    self.Write_Log("Status refresh failed, retrying...", "WARNING")
                    retry_times += 1
                    if retry_times >= 10:
                        self.Write_Log("Retry too much times, closed!", "WARNING")
                        self.instance.state = "failed"
                        self.job.state = "failed"
                        db.session.commit()
                        break
                    continue
                if current_state in ["stopped", "finished"]:
                    time.sleep(2)  # sleep 2秒做双重检查
                    current_state, created, updated = self.get_application_info(self.app_name)
                    if current_state in ["stopped", "finished"]:
                        self.Write_Log('#' * 20)
                        # self.Do_Before_Remove()
                        self.job.state = "finished"
                        self.db.session.commit()
                        break

                elif current_state in ["launching", "starting", "waiting", "restarting"]:
                    self.Write_Log("Task is pending...", "VERBOSE")
                    self.job.state = "waiting"
                    self.db.session.commit()

                elif current_state in ["running", "stopping", "updating", "updated", "scaling", "deleting"]:
                    if not start_running_ok:
                        # step 8 任务开始在容器中运行
                        sleep_time = RUNNING_SLEEP_TIME
                        start_running_ok = True
                        self.Write_Log('*' * 20)
                        self.Write_Log("Task is running now ~", "VERBOSE")
                    self.job.state = "running"
                    self.db.session.commit()

                elif current_state == 'failed':
                    result, info = self.app_info(self.app_name)
                    impl_logger.error("experiment executed failed, related info:{}".format(info))
                    # 不是运行中失败都进行捕捉处理，并且小于最大重试次数才重试
                    if self.job.state != "running" and self.retry_cnt < FAIL_RETRY_MAX_CNT:
                        # 可以捕捉到错误信息，如Unable to find a node that satisfies the following conditions \n[aliyun.gpu=1]
                        # 暂时所有失败一律重试
                        # ok = self.Ensure_Cluster_Resource() # 本身部署成功已占有资源
                        result = self.app_redeploy(self.app_name)
                        impl_logger.info("try to redeploy app:{}, result:{}".format(self.app_name, result))
                        time.sleep((FAIL_RETRY_MAX_CNT - self.retry_cnt) * FAIL_RETRY_INTERVAL)  # 直接睡眠重试时间
                        self.retry_cnt += 1
                        continue  # 继续循环，不进入失败流程
                    # self.Do_Before_Remove()
                    # 进入最终失败流程
                    self.Write_Log("Task is failed. Please try to rerun the task later", "ERROR")
                    self.job.state = current_state
                    self.db.session.commit()
                    break

                else:
                    self.Write_Log("Task is %s" % current_state, "VERBOSE")
                    self.job.state = current_state
                    self.db.session.commit()
            db.session.commit()
            time.sleep(sleep_time)
        return True

    @active_dbmodel(("experiment", "instance"))
    def Mount_Dataset(self):
        '''
        :return:
        '''
        data_volume_index = 0
        for data_nfs_opt in self.data_nfs_opts:
            self.Write_Log("creat data_volume...the dataset will be mounted on directory: /input/%s" %
                           data_nfs_opt["mount_dir"])
            data_volume_result, data_volume_content = self.volume_create(
                name=self.data_name.replace("##INDEX##", str(data_volume_index)),
                driver="nas",
                driverOpts=data_nfs_opt)
            data_volume_index += 1
            if not data_volume_result:
                self.Write_Log("data_volume create failed\n{}".format(data_volume_content),
                               "ERROR")
                return False
            else:
                self.Write_Log("data_volume create successfully, mount dir: /input/%s" % str(data_nfs_opt["mount_dir"]))
        return True

    def Mk_Output_Dir(self):
        # return True
        # TODO: 在nas上写文件
        self.Write_Log("mkdir output")
        try:
            Mkdir_Output(self.job_id)
        except Exception as e:
            self.Write_Log(repr(e), "VERBOSE")
            return False
        try:
            return self.Generator_Run()
        except Exception as e:
            self.Write_Log('\n'.join((repr(e), str(traceback.format_exc()))), "VERBOSE")
            self.Write_Log("Generate run script failed", "ERROR")
            return False

    def Create_Work_Volume(self):
        '''
        创建数据卷，挂载代码到容器的/workspace目录
        :return:
        '''
        try:
            work_volume_result, work_volume_content = self.volume_create(self.work_name, "nas", self.work_nfs_opts)
        except Exception as e:
            self.Write_Log("Request to create Volume failed", "ERROR")
            return False
        if not work_volume_result:
            self.Write_Log("work_volume create failed\n{}".format(work_volume_content), "ERROR")
            return False

        self.Write_Log("work_volume create successfully, mount dir: {}".format(self.WORKING_DIR))  # /workspace
        return True

    @active_dbmodel(("experiment", "user"))
    def Generator_Run(self, sleep_seconds=3):
        '''
        用户应用（任务作业）的entrypoint启动脚本相关。

        1. updated on 2018-02-26
            基于feature/switchuser的方案，将run.sh拆分为main.sh,config.sh,task.sh

        ##########################################################################
        #                         main.sh                                        #
        # This part should:                                                      #
        # 1. run as entrypoint in dockerfile                                     #
        # 2. execute config.sh, and execute task.sh only if the former succeeded #
        ##########################################################################
        ##########################################################################
        #                         config.sh                                      #
        # This part should:                                                      #
        # 1. create a new user, fix the new user's permission problem            #
        # 2. customize jupyter                                                   #
        # 2. execute config.sh, and execute task.sh only if the former succeeded #
        # 3. should be deleted after executed(even if executed failed)           #
        ##########################################################################
        ##########################################################################
        #                         task.sh                                        #
        # This part should:                                                      #
        # 1. remove config.sh by reading a command string from environment,      #
        #    and execute it                                                      #
        # 2. execute user's job                                                  #
        # 3. can be readable in public                                           #
        # 4. install pip dependencies as a daemon in jupyter mode                #
        ##########################################################################
        :param sleep_seconds: main.sh休眠的时间，单位秒
        :return: True or raise exception
        '''
        # fetch necessary info from database
        mode = self.job.mode
        enable_tensorboard = self.job.enable_tensorboard
        auto_command = self.job.command

        # init command list with header
        main_cmd, config_cmd, task_cmd = [self.COMMON_SH_HEADER], [self.COMMON_SH_HEADER], [self.COMMON_SH_HEADER]

        # job executor's home directory, "/root" or "/home/USERNAME"
        container_user_home = "/root" if self.is_run_as_root else "/home/{}".format(self.user.username)

        # create a new user and fix it's permissions
        # For write perm, the user can only write /workspace, where run.sh not included, and it's home directory.
        # For pip, set pip install path to user's home to escape permission problems
        # Note:
        # 1. cat >> << must transfer escape character like '$'
        # 2. fix_perm_file will change run.sh's perm under dir /workspace, so need change it back
        # 3. echo {password} | passwd --stdin {username}
        # 4. "echo \"Cmnd_Alias SQUID = !/bin/su\n{username} ALL=(ALL)  SQUID\" >> /etc/sudoers "
        if not self.is_run_as_root:
            config_cmd.append("cat >> {fix_perm_file} << FIX_PERM_EOF\n{fix_perm_content}\nFIX_PERM_EOF\n"
                              "groupadd -g 1002 {groupname} "
                              " && useradd -r -m -u 1001 -g 1002 {username} "
                              " && echo {username}:{password} | chpasswd "
                              "cp -R ~/.jupyter {home_dir}/ "
                              " && sh {fix_perm_file} {dirs_to_fix_perm}"
                              .format(fix_perm_file="/.fix-permissions.sh",
                                      fix_perm_content=FIX_PERMISSIONS_IN_CONTAINER,
                                      dirs_to_fix_perm=' '.join((self.WORKING_DIR,
                                                                 container_user_home)),
                                      groupname=self.user.username,
                                      username=self.user.username,
                                      working_dir=self.WORKING_DIR,
                                      home_dir=container_user_home,
                                      password=self.user.username))

            # make sure `~/.pip/` and `~/.bashrc` exists
            config_cmd.append("mkdir -p {home_dir}/.pip "
                              " && printf \"[install]\ninstall-option=--prefix=~/.local\" >> {home_dir}/.pip/pip.conf "
                              .format(home_dir=container_user_home))

        # activate environment setting configured by config.sh
        task_cmd.append("source ~/.bashrc")

        # support auto pip install
        if os.path.isfile(os.path.join(self.workdir, "russell_requirements.txt")):
            if mode == "jupyter":
                # install by daemon, and discard stdout and stderr
                pre_command = "pip --default-timeout=1000 install -r russell_requirements.txt > /dev/null 2>&1 &"
            else:
                pre_command = "pip --default-timeout=1000 install -r russell_requirements.txt"
            task_cmd.append(pre_command)

        # support tensorboard daemon service
        # set logdir to our specified output directory
        if enable_tensorboard:
            task_cmd.append("nohup tensorboard "
                            "--logdir={logdir} "
                            "--path_prefix=/tensorboard/{id} &".format(logdir="{}/output".format(self.WORKING_DIR),
                                                                       id=self.job_id))

        # add experiment.command after pip installation finished
        if auto_command:
            task_cmd.append(auto_command)

        if mode == "jupyter":
            # set entry working directory and customize prompt for bash
            config_cmd.append("echo \"{set_default_terminal_dir}\n"
                              "export PS1='\033[1;34m\u@{expname}:\W$ \[\033[0m\]'\" >> {home_dir}/.bashrc"
                .format(
                set_default_terminal_dir=self.SET_DEFAULT_TERMINAL_DIR.format(working_dir=self.WORKING_DIR),
                expname=self.job.project_name,
                home_dir=container_user_home))

            # /bin/bash is not working well enough in notebook terminal, so keep default /bin/sh
            # "export SHELL=/bin/bash "

            # customize jupyter css
            config_cmd.append("mkdir -p {home_dir}/.jupyter/custom "
                              "&& cat >> {home_dir}/.jupyter/custom/custom.css << FIX_NB_CSS_EOF\n"
                              "{jupyter_css}\nFIX_NB_CSS_EOF".format(jupyter_css=JUPYTER_CSS,
                                                                     home_dir=container_user_home))
            # open notebook without token and specified base url,
            # while other configs read from ~/.jupyter/jupyter_notebook_config.py
            config_cmd.append("cat >> {home_dir}/.jupyter/jupyter_notebook_config.py <<FIX_NB_CONF_EOF\n"
                              "{fix_jupyter_notebook_config}\nFIX_NB_CONF_EOF"
                .format(
                home_dir=container_user_home,
                fix_jupyter_notebook_config="\nc.NotebookApp.notebook_dir = '{notebook_dir}'"
                                            "\nc.NotebookApp.token = ''"
                                            "\nc.NotebookApp.base_url = 'notebook/{id}/'"
                                            "\nc.NotebookApp.iopub_data_rate_limit = 1.0e10"
                                            "\nc.NotebookApp.allow_origin = '*'"
                                            "\nc.NotebookApp.allow_credentials = True"
                                            "\nc.NotebookApp.disable_check_xsrf = True"
                                            "\nc.NotebookApp.tornado_settings = {{'headers': {{"
                                            "'Content-Security-Policy': \"frame-ancestors "
                                            "{embbed_sites} 'self' \""
                                            ",'Access-Control-Allow-Headers': \"x-requested-with, Content-Type, Accept-Encoding, Accept-Language, "
                                            "Cookie, Referer, Origin, Accept\"}}}}"
                    .format(notebook_dir=self.WORKING_DIR,
                            id=self.job_id,
                            embbed_sites="localhost:8080 test.russellcloud.com" if self.is_test_env
                            else "russellcloud.com")))

            # When embedding the notebook in a website using an iframe, consider putting the notebook in single-tab
            # mode. Since the notebook opens some links in new tabs by default, single-tab mode keeps the notebook from opening additional tabs.
            # To make nb in iframe can communicate with parent page, we add postMessage javascript code.
            config_cmd.append("cat >> {home_dir}/.jupyter/custom/custom.js << JUPYTER_JS_EOF\n"
                              "{js}\nJUPYTER_JS_EOF"
                              .format(js=self.CUSTOM_JS_FORMAT.format(js_code=self.SINGLE_TAG_JS
                                                                              + "\n"
                                                                              + IFRAME_CUSTOM_JS),
                                      home_dir=container_user_home))

            # # iframe extension
            # nbext_dir = "{}/.ipython/nbextensions".format(container_user_home)
            # config_cmd.append("mkdir -p {nbext_dir} "
            #                   "&& cat >> {nbext_dir}/iframe_extension.js << IFRAME_EOF\n"
            #                   "{js}\nIFRAME_EOF\n".format(nbext_dir=nbext_dir,
            #                                               js=IFRAME_EXTENSION_JS))
            # # enable iframe extension (necessary)
            # config_cmd.append("jupyter nbextension enable --py widgetsnbextension "
            #                   "&& jupyter nbextension install {}/iframe_extension.js"
            #                   "&& jupyter nbextension enable iframe_extension"
            #                   .format(nbext_dir))

            # serving jupyter notebook
            task_cmd.append("/run_jupyter.sh")

        # make main.sh not readable for anyone except it's owner(root)
        # and make config.sh writable for anyone
        config_cmd.append("chmod 500 {} && chmod 766 {}".format(self.main_file,
                                                                self.config_file))
        # sleep for a while first to wait for polling state
        main_cmd.append("sleep {}".format(sleep_seconds))
        # execute config_cmd and task_cmd by `runuser`
        # `su` will create new shell process, and the working directory is /home/$USER)
        # command.append("su - {username} -s /bin/sh << EOF\n{content}\nEOF\n"
        # `sudo` will keep current env but NOT switch to that user actually
        # command.append("sudo -u {username} /bin/sh << EOF\n{content}\nEOF\n"
        main_cmd.append("runuser -u root /bin/bash {}".format(self.config_file))
        # delete config_script_fn before execute `real` task, and unset the `env command`
        # named PREPARE, actually do clean up staff
        # ATTENTION: if put in task.sh instead of main.sh, this command should come top in task.sh
        main_cmd.append("`$PREPARE` && unset PREPARE")
        main_cmd.append("runuser -u {username} /bin/bash {task_fn}".format(
            config_fn=self.config_file,
            task_fn=self.task_file,
            username="root" if self.is_run_as_root else self.user.username))

        # write command to file on disk,
        # and give it executable perm
        main_file, config_file, task_file = \
            os.path.join(self.workdir, self.main_script_fn), \
            os.path.join(self.workdir, self.config_script_fn), \
            os.path.join(self.workdir, self.task_script_fn)
        file_util.write_file('\n'.join(main_cmd), main_file, "w")
        file_util.write_file('\n'.join(config_cmd), config_file, "w")
        file_util.write_file('\n'.join(task_cmd), task_file, "w")
        # 744
        os.chmod(main_file,
                 stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
        return True

    @active_dbmodel(("experiment", "instance"))
    def Get_Configs(self, server='master'):
        testEnv = "False"
        if self.is_test_env:
            testEnv = "True"
            server = "test"
        self.work_name = "work-" + self.app_name

        if self.job.instance_type == GPU_INSTANCE_TYPE:
            gpu_num = 1
            jupyter_url = SERVER_CONFIG_MAP.get(server).get("jupyter_url_g")
            nfs_host = SERVER_CONFIG_MAP.get(server).get("nfs_host_g")
            tb_base_url = SERVER_CONFIG_MAP.get(server).get("tensorboard_url_g")
        else:
            gpu_num = 0
            jupyter_url = SERVER_CONFIG_MAP.get(server).get("jupyter_url_c")
            nfs_host = SERVER_CONFIG_MAP.get(server).get("nfs_host_c")
            tb_base_url = SERVER_CONFIG_MAP.get(server).get("tensorboard_url_c")
        self.work_nfs_opts = {
            "diskid": SERVER_CONFIG_MAP.get(server).get('disk_id'),
            "host": nfs_host,
            "path": "/experiment/" + self.job_id + "/",
            "mode": ""
        }
        self.data_nfs_opts = []
        self.data_name = ""
        data_ids = self.job.data_id_list

        if len(data_ids) > 0:
            self.data_name = "data-" + self.work_name + "-##INDEX##"
            for data_id in data_ids:
                if ':' not in data_id:
                    self.Write_Log("Data config err:%s " % self.job.data_ids, "ERROR")
                    return None, False
                data_id, mount_dir = data_id.split(':')
                self.data_nfs_opts.append({
                    "diskid": SERVER_CONFIG_MAP.get(server).get('disk_id'),
                    "host": nfs_host,
                    "path": "/data/" + data_id + "/",
                    "mode": "",
                    "mount_dir": mount_dir  # not for aliyun
                })
        try:
            self.docker_image_str = self.Get_Docker_Image_Str(str(self.job.environment),
                                                              self.job.instance_type)
        except Exception as e:
            self.Write_Log("get docker image env name failed, reason:{}, {}".format(str(e), traceback.format_exc()),
                           "ERROR")
        if not self.docker_image_str:
            self.Write_Log("No environment:%s " % self.job.environment, "ERROR")
            return False
        self.Write_Log("experiment env: {}".format(self.job.environment))

        # step 4 获取容器等配置
        with open('Platform/ERACenter/Cloud_Interface/aliyun_docker/yaml/tensorflow.yaml', 'r') as f:
            content = f.read().format

        data_volume_num = len(self.data_nfs_opts)
        if data_volume_num > 0:
            dataset_volumes = '\n    '.join(["- {volume_name}:/input/{mount_dir}"
                                            .format(volume_name=self.data_name.replace("##INDEX##", str(i)),
                                                    mount_dir=self.data_nfs_opts[i]["mount_dir"])
                                             for i in range(data_volume_num)])
        else:
            dataset_volumes = ""

        influxdb_api_uri = Influxdb_Controler.get_influxdb_api_uri(self.cluster_ist.cluster_id)
        if not influxdb_api_uri:
            self.Write_Log("failed to get influxdb_api_uri from redis...", "VERBOSE")
            influxdb_api_uri = ""

        # script filename write on nas
        self.main_script_fn, self.config_script_fn, self.task_script_fn = \
            ".{}_main.sh".format(self.job_id), \
            ".{}_config.sh".format(self.job_id), \
            ".{}_task.sh".format(self.job_id)
        self.main_file, self.config_file, self.task_file = \
            self.WORKING_DIR + '/' + self.main_script_fn, \
            self.WORKING_DIR + '/' + self.config_script_fn, \
            self.WORKING_DIR + '/' + self.task_script_fn

        self.content = content(
            service_name="{}user-era-application".format("test-" if self.is_test_env else ""),
            nb_port=8888,
            tb_port=6006,
            id=self.job_id,
            testEnv=testEnv,
            is_always_restart="no",
            scale_num=1,
            nb_url=jupyter_url + self.job_id + "/",
            tb_url=tb_base_url + self.job_id,
            image=self.docker_image_str,
            gpu_num=gpu_num,
            work_volumes_name=self.work_name,
            dataset_volumes=dataset_volumes,
            run_sh=self.main_file,
            cleanup_cmd="rm -rf {}".format(self.config_file),
            mem_limit=machine_resource_limit.get(self.job.instance_type,
                                                 machine_resource_limit.get(CPU_INSTANCE_TYPE))["memory"],
            influxdb_api_uri=influxdb_api_uri
        )
        return True

    def Init_Aliyun(self):
        ok = self.Ensure_Cluster_Resource()
        if not ok:
            self.Write_Log("Getting machine resource failed")
            return False
        ok = self.Get_Configs()
        if not ok:
            self.Write_Log("Get Configurations failed", "ERROR")
            return False

        #### Make output dir and generate run.sh
        ok = self.Mk_Output_Dir()
        if not ok:
            return False

        ok = self.Create_Work_Volume()
        if not ok:
            return False

        if self.data_name != "":
            ok = self.Mount_Dataset()
            if not ok:
                return False
        return True

    @active_dbmodel(("experiment"))
    def Init_Task(self):
        # TODO: 通过nas操作文件
        module = Get_Code_Module(id=self.job.code_id)
        if not module:
            self.Write_Log("Module not found", "ERROR")
            return False
        #### Copy files from archive to experiment environment ###
        if not Is_Existed_Experiment(self.job_id):
            if not Import_Module_To_Experiment(experiment_id=self.job_id, module_id=module.id):
                self.Write_Log("import module to experiment failed", "ERROR")
                return False
        else:
            self.Write_Log("Existed experiment, dir: /root/workspace/experiment/{}".format(self.job_id),
                           "VERBOSE")
        return True

    @staticmethod
    def Get_Docker_Image_Str(env, instance_type):
        if not env or not isinstance(env, str):
            return False
        DOCKER_IMAGE_CONFIG.refresh()
        print("debug", "dockerimage", DOCKER_IMAGE_CONFIG.get("cpu").get("caffe"))
        gpu_cpu = "gpu" if instance_type == GPU_INSTANCE_TYPE else "cpu"
        image_tag = DOCKER_IMAGE_CONFIG.get(gpu_cpu).get(env)
        return DOCKER_PRE + image_tag if image_tag else None

    @active_dbmodel(("experiment",))
    def Pay_Bill(self):
        return Billing(owner_id=self.job.owner_id,
                       category=self.job.instance_type_trimmed,
                       from_id=self.job.module_id,
                       dosage=self.job.duration)


DATA_DIR = '/root/workspace/data'
EXPERIMENT_DIR = '/root/workspace/experiment'
MODULE_DIR = '/root/workspace/module'


def Billing(owner_id, category, from_id, dosage):
    return True


def Is_Existed_Experiment(experiment_id):
    path = os.path.join(EXPERIMENT_DIR, str(experiment_id))
    if os.path.isdir(path):
        return True
    else:
        return False


def Import_Data_To_Experiment(experiment_id, data_id):
    source = DATA_DIR + str(data_id)
    target = EXPERIMENT_DIR + str(experiment_id) + "/input/"
    return file_util.copy_dir(source, target)


def Import_Module_To_Experiment(experiment_id, module_id):
    source = os.path.join(MODULE_DIR, str(module_id))
    target = os.path.join(EXPERIMENT_DIR, str(experiment_id))
    return file_util.copy_dir(source, target)


def Mkdir_Output(experiment_id):
    dirname = os.path.join(EXPERIMENT_DIR, str(experiment_id), "output")
    if not os.path.exists(dirname):
        os.mkdir(dirname)
