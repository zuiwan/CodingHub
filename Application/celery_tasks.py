#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Library.OrmModel.User import User
from Library.OrmModel.Project import Project
from Library.OrmModel.TaskInstance import TaskInstance
from Library.OrmModel.Task import Task
from Library.OrmModel.Module import Module
from app import flask_app
from Library.extensions import orm, celery_app
from Library.Utils import *
from time import sleep
import os, random
import json
import time,stat


data_dir = flask_app.config['UPLOAD_DATA_FOLDER']
experiment_dir = flask_app.config['UPLOAD_EXPERIMENT_FOLDER']
module_dir = flask_app.config['UPLOAD_MODULE_FOLDER']
def Import_Data_To_Task(task_id, data_id):
    # type: (str, str) -> bool
    source = data_dir + str(data_id)
    target = experiment_dir + str(task_id) + "/input/"
    return copy_dir(source,target)


def Import_Module_To_Task(task_id, module_id):
    # type: (str, str) -> bool
    source = module_dir + str(module_id)
    target = experiment_dir + str(task_id)
    return copy_dir(source,target)


def Outport_To_Data(task_id, data_id):
    # type: (str, str) -> bool
    source = experiment_dir + str(task_id) + "/output"
    target = data_dir + str(data_id)
    return copy_dir(source,target)

def Mkdir_Output(task_id):
    os.mkdir(experiment_dir + str(task_id) + "/output")

def Write_Celery_Log(task_id, log_str, level='INFO'):
    log_path = flask_app.config['UPLOAD_LOG_FOLDER'] + task_id + "/worker.log"
    line = Celery_Log_Line(log_str, level)
    write_file(line, log_path)
    
def Generator_Run(task_id, auto_command, mode):
    command = "#!/bin/sh\n"

    command = command + "sleep 1\n"
    if os.path.isfile(flask_app.config['UPLOAD_EXPERIMENT_FOLDER']+ str(task_id) + "/russell_requirements.txt"):
        if mode == "jupyter":
            pre_command = "pip --default-timeout=1000 install -r russell_requirements.txt &\n"
        else:
            pre_command = "pip --default-timeout=1000 install -r russell_requirements.txt \n"
        command = command + pre_command
        # command = 'sh -c \'{}&&{}\''.format(pre_command, command)
    command = command + auto_command + "\n"
    if mode == "jupyter":
        command = command + "jupyter notebook --NotebookApp.token= --NotebookApp.base_url={}\n".format(task_id)
    write_file(command, flask_app.config['UPLOAD_EXPERIMENT_FOLDER'] + str(task_id) + "/run.sh")
    os.chmod(flask_app.config['UPLOAD_EXPERIMENT_FOLDER'] + str(task_id) + "/run.sh", stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

def gen_run_py_shell(task_id, auto_command, mode):
    command = "#!/bin/sh\n"

    command = command + "sleep 1\n"
    if os.path.isfile(flask_app.config['UPLOAD_EXPERIMENT_FOLDER']+ str(task_id) + "/codinglife_requirements.txt"):
        if mode == "jupyter":
            pre_command = "pip --default-timeout=1000 install -r russell_requirements.txt &\n"
        else:
            pre_command = "pip --default-timeout=1000 install -r russell_requirements.txt \n"
        command = command + pre_command
        # command = 'sh -c \'{}&&{}\''.format(pre_command, command)
    command = command + auto_command + "\n"
    if mode == "jupyter":
        command = command + "jupyter notebook --NotebookApp.token= --NotebookApp.base_url={}\n".format(task_id)
    write_file(command, flask_app.config['UPLOAD_EXPERIMENT_FOLDER'] + str(task_id) + "/run.sh")
    filename = flask_app.config['UPLOAD_EXPERIMENT_FOLDER'] + str(task_id) + "/run.sh"
    os.chmod(filename, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
    return filename

def run_shell_right_row(path):
    import subprocess
    output = subprocess.check_output([path])
    return output

@celery_app.task()
def run_task_asyn(task_id):
    task = Task.query.get(task_id)
    lan = task.lan
    if lan not in flask_app.config['ALLOWED_EXTENSIONS']:
        return False
    if lan == 'py':
        result = run_shell_right_row(gen_run_py_shell(task_id=task_id, auto_command=task.command, mode=task.mode))
        return result
    elif lan == 'c':
        pass
    elif lan == 'cpp':
        pass

def check_instance(task_id):
    # step 2 celery任务开始执行 #
    task = Task.query.get(task_id)
    Write_Celery_Log(task.id, "Celery task start being excuted")
    module = Module.query.get(task.module_id)
    Import_Module_To_Task(task.id, module_id=module.id)

    # some long running task here
    state = "waiting"
    experiment = Experiment.query.get(task_id)
    module = Module.query.get(experiment.module_id)
    Import_Module_To_Experiment(task_id=task_id, module_id=module.id)

    log_path = flask_app.config['UPLOAD_LOG_FOLDER'] + task_id
    os.mkdir(log_path)

    log_name = log_path + "/worker.log"
    clog_name = log_path + "/container.log"
    clog_length = 0

    Mkdir_Output(task_id)
    name = experiment.name.replace("/","_").replace(":","_")

    user_path = '/workspace'
    if module.mode == "jupyter":
        port = getPort()
    else:
        port = None
    Write_Celery_Log("start container........................\n", clog_name)

    service_id = myService.create(image=module.default_container,
                               name=name,
                               source=flask_app.config['UPLOAD_EXPERIMENT_FOLDER']+task_id,
                               target=user_path,
                               command=module.command,
                               workdir=user_path,
                               run_mode=module.mode,
                                port=port,
                                task_id=task_id)
    log_id = service_id
    log(" create service, service id:{}, Experiment id: {}\n".format(service_id,task_id),log_path=log_name)
    instance = TaskInstance(container=module.default_container, log_id=log_id, owner_id=experiment.owner_id,
                            instanceType=experiment.instance_type, label=experiment.name, module_id=module.id,
                            mode=module.mode, state=state, version=experiment.version,outputs=log_id)

    db.session.add(instance)
    db.session.commit()
    experiment.task_instance_ids = instance.id
    db.session.commit()

    log("##################################################################################\n", clog_name)

    i = 0
    while True:
        try:
            log("check service, service_id:{}\n".format(service_id),log_path=log_name)
            current_state = myService.get_stats(service_id)
            # experiment = Experiment.query.get(task_id)
            # instance = TaskInstance.query.get(experiment.task_instance_ids)
        except:
            if instance.state not in ["waiting","pending"]:
                # if no service while state not in waiting, success?
                log("service has failed ,experiment state: {}\n".format(experiment.state),log_path=log_name)
                instance.state = "failed"
                experiment.state = "failed"
                db.session.commit()
                break
            else:
                # if i>=10:
                #     log("service has wait too long ,system shutdown",log_name)
                #     break
                # else:
                log("service is waiting\n",log_name)
        else:
            log("service is {} ,experiment state: {}\n".format(current_state,experiment.state),log_name)

            if experiment.state == "shutdown":
                log("service is shutdown ,experiment state: {}\n".format(service_id, experiment.state),
                    log_name)
                doBeforeRemove(experiment,instance)
                myService.stop(service_id)
                break
            if current_state :
                if current_state == "complete":
                    new_state = "success"
                    instance.state = new_state
                    experiment.state = new_state
                    db.session.commit()

                    try:
                        log_list = get_container_logs(myService=myService,service_id=service_id)
                    except Exception,e:
                        log("container log timeout,{}\n".format(str(e)),log_name)
                        print e
                    else:
                        while clog_length < len(log_list):
                            log(log_list[clog_length],clog_name)
                            clog_length+=1


                    doBeforeRemove(experiment,instance)
                    log("##################################################################################\n",
                        clog_name)
                    log("task finished, service closed\n", clog_name)
                    myService.stop(service_id)
                    break
                elif current_state in ["pending","ready","assigned","preparing","waiting"]:
                    i += 1
                    if i >= 10:
                        log("service has wait too long ,failed\n",log_name)
                        break
                elif current_state == "running":

                    try:
                        log_list = get_container_logs(myService=myService,service_id=service_id)
                    except Exception,e:
                        log("container log timeout,{}\n".format(str(e)),log_name)
                        print e
                    else:
                        while clog_length < len(log_list):
                            log(log_list[clog_length],clog_name)
                            clog_length+=1

                    if instance.mode == "jupyter":
                        task_id = task_id
                        if not JupyterToken.query.filter_by(task_id=task_id).first():
                            log("regist,task_id:{}\n".format(task_id),log_name)
                            registJupyter(task_id=task_id,port=port)
                    if experiment.state in ["pending","ready","assigned","preparing","waiting"]:
                        instance.state = current_state
                        experiment.state = current_state
                        experiment.started = db.func.current_timestamp()
                        db.session.commit()
                else:
                    instance.state = current_state
                    experiment.state = current_state
                    db.session.commit()

                    try:
                        log_list = get_container_logs(myService=myService,service_id=service_id)
                    except Exception,e:
                        log("container log timeout,{}\n".format(str(e)),log_name)
                        print e
                    else:
                        while clog_length < len(log_list):
                            log(log_list[clog_length],clog_name)
                            clog_length+=1

                    doBeforeRemove(experiment,instance)
                    myService.stop(service_id)
                    break

        db.session.commit()
        sleep(3)

def getLogNum(id):
    logGen = myService.get_logs(id)
    return len(list(logGen))


def getJupyterToken(service_id):
    try:
        logGen = myService.get_logs(service_id)
    except:
        return None
    else:
        logList = list(logGen)
        logLast = logList[-1]
        if 'token=' in logLast:
            logLastList = logLast.split('token=')
            jupyter_token = logLastList[1].strip()
            if len(jupyter_token) > 0:
                return jupyter_token
        return None


def doBeforeRemove(experiment,instance):

    # save logs

    # save output to data
    experiment.ended = db.func.current_timestamp()
    data = Data(name=experiment.name+"_"+str(experiment.version)+"_output",description="task_id:{}".format(experiment.id),permission=experiment.permission,version=1,family_id=experiment.family_id)
    db.session.add(data)
    db.session.commit()
    Outport_To_Data(task_id=experiment.id, data_id=data.id)
    instance.outputs = data.id

    # experiment.output_id
    return



def getPort():
    pscmd = "netstat -ntl |grep -v Active| grep -v Proto|awk '{print $4}'|awk -F: '{print $NF}'"
    procs = os.popen(pscmd).read()
    procarr = procs.split("\n")
    tt= random.randint(20000, 30000)
    if tt not in procarr:
        return tt
    else:
        getPort()


def registJupyter(task_id,port):
    proxy_utils.add_proxy(task_id=task_id, port=port)
    jupyterToken = JupyterToken(task_id=task_id, jupyter_token="", port=port, state="open")
    db.session.add(jupyterToken)
    db.session.commit()
