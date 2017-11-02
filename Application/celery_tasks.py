#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Library.extensions import orm as db
from Library.extensions import celery_app
from Library.log_util import LogCenter
from Library.file_util import *
celery_logger = LogCenter.instance().get_logger('celery', 'tasks')


@celery_app.task(bind=True)
@check_api_cost_time
def checkInstance(self, experiment_id, time_limit=None):
    # step 2 celery任务开始执行 #
    Write_Celery_Log(experiment_id, k_log_output_2)

    experiment = Get_Experiment_By_Id(experiment_id)
    if not experiment:
        Write_Celery_Log(experiment_id, "Experiment not found", "ERROR")
        return

    module = Get_Module_By_Id(experiment.module_id)
    if not module:
        Write_Celery_Log(experiment_id, "Module not found", "ERROR")
        return

    if experiment.data_id:
        if not Get_Dataset_By_Id(experiment.data_id):
            Write_Celery_Log(experiment.id, "Dataset not found", "ERROR")
            return

    #### Copy files from archive to experiment environment ###
    Import_Module_To_Experiment(experiment_id=experiment_id, module_id=module.id)

    #### Get Configs ####
    configs = Get_Configs(experiment, module)
    if configs is None:
        Write_Celery_Log(experiment_id, "Get Configurations failed", "ERROR")
        return
    _application = configs.get('_application')
    work_nfs_opts = configs.get('work_nfs_opts')
    data_nfs_opts = configs.get('data_nfs_opts')
    work_name = configs.get('work_name')
    data_name = configs.get('data_name')
    name = configs.get('name')
    content = configs.get('content')
    docker_image = configs.get('docker_image')
    #### Get Configs ####

    #### Make output dir and generate run.sh
    flag = Mk_Output_Dir(experiment_id=experiment_id, module_command=module.command, module_mode=module.mode)
    if not flag:
        return False

    flag = Create_Work_Volume(experiment_id=experiment_id,
                       work_name=work_name,
                       work_nfs_opts=work_nfs_opts,
                       _application=_application)
    if not flag:
        return False

    if data_name != "":
        flag = Mount_Dataset(experiment_id=experiment_id,
                      data_name=data_name,
                      data_nfs_opts=data_nfs_opts,
                      _application=_application)
        if not flag:
            return False

    state = "waiting"

    ### 创建任务实例
    instance = Create_TaskInstance(container=docker_image,
                                   log_id=experiment_id,
                                   owner_id=experiment.owner_id,
                                   instance_type=experiment.instance_type,
                                   label=name,
                                   module_id=module.id,
                                   mode=module.mode,
                                   state=state,
                                   version=experiment.version)

    ### 更新experiment表的实例
    Update_Experiment(experiment_id, task_instance_ids=instance.id)

    # step 7 任务创建成功或失败
    application_result, application_content = _application.app_create(name, template=content)
    if application_result:
        Write_Celery_Log(experiment_id, k_log_output_7, "VERBOSE")
    else:
        Write_Celery_Log(experiment_id, "Task create failed" + application_content, "ERROR")
        return

    try:
        current_state, created, updated = _application.get_application_info(name)
        datetime_to_stop = string_toDatetime(created) + datetime.timedelta(seconds=time_limit or 0)
    except:
        datetime_to_stop = None
    ###### 轮询 ######
    PollingState(experiment=experiment,
                 instance=instance,
                 name=name,
                 _application=_application,
                 datetime_to_stop=datetime_to_stop)



@celery_app.task(bind=True)
def fork_project_task(self, old_path, new_path, project_id):
    if copy_dir(old_path, new_path):
        project.status = 'normal'
        db.session.commit()
        return True
    else:
        project.status = 'failed'
        db.session.commit()
        self.update_state(state='FAILURE', meta={'status': 'Copy Failed, source does not existed.'})
        return False

@celery_app.task(bind=True)
def clone_project_task(self, project_dir, step='compress'):
    imz = InMemoryZip()
    num = 0
    for root, dirs, files in os.walk(project_dir):
        for name in files:
            filepath = os.path.join(root, name)
            imz.appendFile(filepath)
            num += 1
            size = os.path.getsize(filepath)
            self.update_state(state='Started', meta={'num': num, 'size': size})
    return imz, num
