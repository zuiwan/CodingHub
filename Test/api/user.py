#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import random
import os
from test.api import REST_API_Test, access_tokens
from test.test_log_util import LogCenter
user_test_logger = LogCenter.instance().get_logger(name="user")



class UserAPI_Test(REST_API_Test):

    def __init__(self):
        self.url = "/api/v1/{user_name}/user/{project_name}"
        super(UserAPI_Test, self).__init__()


    def run(self):
        user_test_logger.info('#'*3 + " [Project] Start Running " + '#' * 3)
        self.__run__() # super
        self.clone()
        self.fork()
        user_test_logger.info('#' * 3 + " [Project] End Running " + '#' * 3)

    def get(self):
        user_test_logger.info('#' * 3 + " [Project] [GET] Start Running " + '#' * 3)
        user_names = self.db.get_user_names()
        project_names = self.db.get_project_names()
        for at in access_tokens:
            for user_name in user_names:
                for project_name in project_names:
                    is_owned = "not " if self.db.is_owned_by_username("project", {"name": project_name}, user_name) else ""
                    user_test_logger.info('*'*3
                                             + " [DATA-RELATION] project:"
                                             + project_name
                                             + " is "
                                             + is_owned
                                             + "owned by user:"
                                             + project_name
                                             + '*'*3)
                    # ?content = head
                    resp_head = self.request("GET",
                                 url=self.url.format(user_name=user_name, project_name=project_name),
                                 params={'content': 'head'},
                                 access_token=at)
                    # ?content = basic
                    resp_basic = self.request("GET",
                                 url=self.url.format(user_name=user_name, project_name=project_name),
                                 params={'content': 'basic'},
                                 access_token=at)
                    # ?content = readme_path
                    resp_readme_path = self.request("GET",
                                 url=self.url.format(user_name=user_name, project_name=project_name),
                                 params={'content': 'readme_path'},
                                 access_token=at)
                    # ?content = readme_body
                    resp_readme_body = self.request("GET",
                                 url=self.url.format(user_name=user_name, project_name=project_name),
                                 params={'content': 'readme_body'},
                                 access_token=at)
                    # ?content = fork - list
                    resp_fork_list = self.request("GET",
                                 url=self.url.format(user_name=user_name, project_name=project_name),
                                 params={'content': 'fork-list'},
                                 access_token=at)
                    # ?content = star - list
                    resp_star_list = self.request("GET",
                                 url=self.url.format(user_name=user_name, project_name=project_name),
                                 params={'content': 'star-list'},
                                 access_token=at)
        user_test_logger.info('#' * 33 + " [Project] [GET] End Running " + '#' * 33)

    def put(self):
        user_test_logger.info('#' * 33 + " [Project] [PUT] Start Running " + '#' * 33)
        user_name = get_user_name_random()
        project_name = get_project_name_random()
        new_project_data = dict.fromkeys(
            ["permission", "description", "family_id", "default_env", "tags", "fork_from_id"]
        )
        self.request("PUT",
                     url=self.url.format(user_name=user_name, project_name=project_name),
                     data=new_project_data)
        user_test_logger.info('#' * 33 + " [Project] [PUT] End Running " + '#' * 33)

    def post(self):
        '''
        1. request.data data={'id','latest_version','permission','description','name','family_id','default_env','tags'}。其中id可为空(project的id)。
2. data['action'] = 'star':  当前登录用户star本API的URL中定位的project。
        :return:
        '''
        user_test_logger.info('#' * 33 + " [Project] [POST] Start Running " + '#' * 33)
        post_data = dict.fromkeys(['id',
                                   'latest_version',
                                   'permission',
                                   'description',
                                   'name','family_id',
                                   'default_env',
                                   'tags',
                                   'action'])
        resp = self.request("POST",
                            url=self.url.format(user_name=get_user_name_random(),project_name=get_project_name_random()),
                            data=post_data)
        user_test_logger.info('#' * 33 + " [Project] [POST] End Running " + '#' * 33)

    def delete(self):

        user_test_logger.info('#' * 33 + " [Project] [DELETE] Start Running " + '#' * 33)
        resp = self.request("DELETE",
                            url=self.url.format(user_name=get_user_name_random(), project_name=get_project_name_random()))

        user_test_logger.info('#' * 33 + " [Project] [DELETE] End Running " + '#' * 33)

    def clone(self):
        """
        Download and optionally untar the tar file from the given url
        """
        user_test_logger.info('#' * 33 + " [Project] [CLONE] Start Running " + '#' * 33)
        url = "/api/v1/projects/clone/{}".format(get_project_id_random())
        try:
            project_name = get_project_name_random()

            self.download_compressed(url,
                                     compression="zip",
                                     uncompress=True,
                                     delete_after_uncompress=False,
                                     dir=project_name)
        except Exception as e:
            user_test_logger.error("Download URL ERROR! {}".format(e))
            return False
        user_test_logger.info('#' * 33 + " [Project] [CLONE] End Running " + '#' * 33)

    def fork(self):
        user_test_logger.info('#' * 33 + " [Project] [FORK] Start Running " + '#' * 33)
        url = "/api/v1/projects/fork/{}".format(get_project_id_random())
        try:
            self.request("GET", url)
        except:
            user_test_logger.error("fork error")
        user_test_logger.info('#' * 33 + " [Project] [FORK] Start Running " + '#' * 33)


class ProjectsAPI_Test_Test(REST_API_Test):
        """
        Test to interact with projects api
        """

        def __init__(self):
            self.url = "/api/v1/projects"
            super(ProjectsAPI_Test_Test, self).__init__()

        def run(self):
            self.__run__()
            self.explore()


        def get(self):
            user_test_logger.info('#' * 3 + " [Projects] [GET] Start Running " + '#' * 3)
            user_names = self.db.get_user_names()
            project_names = self.db.get_project_names()
            for at in access_tokens:
                for user_name in user_names:
                    for project_name in project_names:
                        # number test
                        self.request("GET",
                                     url=self.url,
                                     params={"username": user_name, "number": random.randint(-10, sys.maxint)})
                        # start_at test
                        self.request("GET",
                                     url=self.url,
                                     params={"username": user_name, "start_at": random.randint(-10, sys.maxint)})
                        # rank_by test
                        self.request("GET",
                                     url=self.url,
                                     params={"username": user_name, "rank_by": random.randint(-10, 10)})
                        # permission test
                        self.request("GET",
                                     url=self.url,
                                     params={"username": user_name, "permission": random.randint(-10, 10)})
                        # filter test
                        filters = ['fork', 'star', 'watch', '', 'errtst']
                        self.request("GET",
                                     url=self.url,
                                     params={"username": user_name, "filter": filters[random.randint(0, 4)]})

            user_test_logger.info('#' * 3 + " [Projects] [GET] End Running " + '#' * 3)

        def explore(self):
            user_test_logger.info('#' * 3 + " [Projects] [EXPLORE] Start Running " + '#'*3)
            url = "/api/v1/projects/explore"
            self.request("GET",
                         url=url,
                         params={})
            user_test_logger.info('#' * 3 + " [Projects] [EXPLORE] Start Running " + '#'*3)
