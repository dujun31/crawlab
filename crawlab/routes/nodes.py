from constants.task import TaskStatus
from db.manager import db_manager
from routes.base import BaseApi
from utils import jsonify
from utils.node import update_nodes_status


class NodeApi(BaseApi):
    col_name = 'nodes'

    arguments = (
        ('name', str),
        ('description', str),
        ('ip', str),
        ('port', str),
    )

    def get(self, id=None, action=None):
        # action by id
        if action is not None:
            if not hasattr(self, action):
                return {
                           'status': 'ok',
                           'code': 400,
                           'error': 'action "%s" invalid' % action
                       }, 400
            return getattr(self, action)(id)

        # get one node
        elif id is not None:
            return db_manager.get('nodes', id=id)

        # get a list of items
        else:
            # get a list of active nodes from flower and save to db
            update_nodes_status()

            # iterate db nodes to update status
            nodes = db_manager.list('nodes', {})

            return {
                'status': 'ok',
                'items': jsonify(nodes)
            }

    def get_spiders(self, id=None):
        items = db_manager.list('spiders')

    def get_deploys(self, id):
        items = db_manager.list('deploys', {'node_id': id}, limit=10, sort_key='finish_ts')
        deploys = []
        for item in items:
            spider_id = item['spider_id']
            spider = db_manager.get('spiders', id=str(spider_id))
            item['spider_name'] = spider['name']
            deploys.append(item)
        return {
            'status': 'ok',
            'items': jsonify(deploys)
        }

    def get_tasks(self, id):
        items = db_manager.list('tasks', {'node_id': id}, limit=10, sort_key='create_ts')
        for item in items:
            spider_id = item['spider_id']
            spider = db_manager.get('spiders', id=str(spider_id))
            item['spider_name'] = spider['name']
            _task = db_manager.get('tasks_celery', id=item['_id'])
            if _task:
                item['status'] = _task['status']
            else:
                item['status'] = TaskStatus.UNAVAILABLE
        return {
            'status': 'ok',
            'items': jsonify(items)
        }
