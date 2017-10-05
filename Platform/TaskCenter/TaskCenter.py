from TaskDBM import TaskDBM
from Library.singleton import Singleton
from Library.log_util import LogCenter

@Singleton
class TaskCenter(object):
    def __init__(self):
        self.logger = LogCenter.instance().get_logger('CerCenterLog')
        self.taskDBM = TaskDBM.instance()

    def run(self, data):
        # data = json.loads(request.data, encoding="utf-8")
        name = data.get('name')
        instance_type = data.get('instance_type')
        data_id = data.get('data_id')
        family_id = data.get('family_id')
        version = data.get('version')
        module_id = data.get('module_id')
        owner_id = data.get('user_id')
        description = data.get('description')
        project_id = data.get("project_id")
        log_id = module_id

        _id = self.taskDBM.insert_task(name=name,
                                 instance_type=instance_type,
                                 dataset_id=data_id,
                                 family_id=family_id,
                                 version=version,
                                 module_id=module_id,
                                 description=description,
                                 owner_id=owner_id,
                                 log_id=log_id,
                                 project_id=project_id)

        # task = Task(name=name, instance_type=instance_type, data_id=data_id, family_id=family_id,
        #                         version=version, module_id=module_id, description=description, owner_id=g.user.id,
        #                         log_id=log_id, project_id=module.project_id)
        # db.session.add(experiment)
        # db.session.commit()

        from Application.celery import run_shell_right_row, gen_run_py_shell
        command = ''
        mode = ''
        result = run_shell_right_row(gen_run_py_shell(_id, auto_command=command, mode=mode))

        return result