#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Library.extensions import (
    celery_app,
    orm as db
)
from Library.Utils.log_util import (
    LogCenter,
    check_api_cost_time
)
from Library.Utils.file_util import *
from Library.Utils.time_util import *

celery_logger = LogCenter.instance().get_logger('celery', 'tasks')


@celery_app.task(bind=True)
@check_api_cost_time
def checkInstance(self, experiment_id, time_limit=None):
    pass


@celery_app.task(bind=True)
def fork_project_task(self, old_path, new_path, project_id):
    if copy_dir(old_path, new_path):
        return True
    else:
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
