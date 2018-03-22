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
celery_logger = LogCenter.instance().get_logger('celery', 'tasks')


@celery_app.task
@check_api_cost_time
def checkInstance(self, job_id, time_limit=None):
    pass
