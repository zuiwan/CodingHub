from kombu import Queue

celery_queues = (
    Queue('file', exchange='file', routing_key='task.user.file.#'),
    Queue('cpu', exchange='user', routing_key='task.user.compute.cpu'),
    Queue('gpu', exchange='user', routing_key='task.user.compute.gpu'),
    Queue('sys', exchange='sys',routing_key='task.sys.#')
)


# CELERY_ROUTES = {
#     'App.celery_api.forkProject': {
#         'queue': 'file',
#         'routing_key': 'task.user.file.#'
#     },
# }