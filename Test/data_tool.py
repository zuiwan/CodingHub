#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
from App.model.module import Module
from App.model.user import User
from App.model.profile import UserProfile
from App.model.experiment import Experiment
from App.model.project import Project
from App.model.data import Data
from App.controler.project import _filter_projects_from_modules, Create_Project, _Get_Project, Update_Project_Setting
from App.controler.module import _Get_Modules, Update_Module_Setting
from App.controler.user import *
from App.common.data_utils import *
from App.extensions.qiniu.setting import *
from six import reraise as raise_

def test_common_get_random_image():
    from App.controler.common import Get_Random_Image
    try:
        image = Get_Random_Image()
        print image.id, image.url, image.usage
    except Exception as e:
        print 'exception'
        traceback = sys.exc_info()[2]
        # print traceback
        raise_(e, None, traceback)

def fill_experiments_project_id():
    experiments = Experiment.query.all()
    for experiment in experiments:
        module = Module.query.filter_by(id=experiment.module_id).first()
        if module:
            project = Project.query.filter_by(id=module.project_id).first()
            experiment.project_id = project.id if project else None
            print 'experiment.project_id added, ', experiment.project_id
    db.session.commit()

def change_mysql_coding():
    import MySQLdb
    host = "localhost"
    passwd = "RussellCloud2017"
    user = "root"
    dbname = "Russell"

    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=dbname)
    cursor = db.cursor()

    cursor.execute("ALTER DATABASE `%s` CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci'" % dbname)

    sql = "SELECT DISTINCT(table_name) FROM information_schema.columns WHERE table_schema = '%s'" % dbname
    cursor.execute(sql)

    results = cursor.fetchall()
    for row in results:
      sql = "ALTER TABLE `%s` convert to character set DEFAULT COLLATE DEFAULT" % (row[0])
      cursor.execute(sql)
    db.close()

def modules2projects():
    projects = _filter_projects_from_modules(Module.query.all())
    for project in projects:
        project.latest_version = project.version
        proj = Create_Project(name=project.name,
                              owner_id=project.owner_id,
                              default_env=project.default_env,
                              description=project.description,
                              family_id=project.family_id)
        print "New project created, it's id = ", proj.id

def get_qiniu_image_url_list():
    # 前缀
    prefix = 'image'
    # 列举条目
    # limit = 10
    limit = None
    # 列举出除'/'的所有文件以及以'/'为分隔的所有前缀
    delimiter = None
    # 标记
    marker = None
    ret, eof, info = bucket.list(k_bucket_name, prefix, marker, limit, delimiter)
    urls = []
    if info.exception == None:
        for item in ret['items']:
            # item['fsize']
            urls.append(k_bucket_url_domain + '/' + item['key'])
    # assert len(ret.get('items')) is not None
    return urls

def create_all_images():
    urls = get_qiniu_image_url_list()
    for url in urls:
        image = Create_Image(url)
        if image:
            print 'success', image.id, image.url
    db.session.commit()
def fill_projects():
    projects = Project.query.all()
    for project in projects:
        image = Get_Random_Image()
        Update_Project_Setting(project.id,
                               latest_version=None,
                               name=None,
                               description=None,
                               permission=None,
                               default_env=None,
                               family_id=None,
                               tags=None,
                               bg_url_id=image.id if image else None)
        print 'update bg-url-id', project.id
def fill_profiles():
    import random
    orgs = ('hust','pkj','org','dian','by','unique')
    citys = ('wuhan','bj','sh','hz','gz','tj')
    phones = ('123525342','45362450','1427937221','1235253443534534542','4536243575750','142793722111')
    bios = ("i'm happy", " i'm not happy", "fat girl", "fat boy", "slim figure", "america demo")
    bg_urls = get_qiniu_image_url_list()
    users = User.query.all()
    for user in users:
        rand_org = orgs[random.randint(0, 5)]
        rand_city = citys[random.randint(0, 5)]
        rand_bio = bios[random.randint(0, 5)]
        rand_phone = phones[random.randint(0,5)]
        rand_bg_url = bg_urls[random.randint(0, len(bg_urls) - 1)]
        image = Create_Image(rand_bg_url, user.id)
        profile = Create_User_Profile(owner_id=user.id,
                                      nickname=user.username,
                                      organization=rand_org,
                                      bio=rand_bio,
                                      city=rand_city
                                      )
        if not profile:
            # existed, update

            profile = Update_User_Profile(id=user.id,
                                nickname=user.username,
                                phone=rand_phone,
                                organization=rand_org,
                                bio=rand_bio,
                                city=rand_city,
                                bg_url_id=image.id)
        print "New profile created, it's id = ", profile.id

def fill_data_image():
    from App.model.image import Image
    datas = Data.query.all()
    bgs = Image.query.all()
    for data in datas:
        data.bg_url_id = random.choice(bgs).id
        db.session.commit()
        print 'bg url added.', data.bg_url_id

def fill_modules_project_id():
    modules = Module.query.all()
    for module in modules:
        # project = _get_project(project_name=module.name, owner_id=module.owner_id)
        project = Project.query.filter_by(name=module.name, owner_id=module.owner_id).first()
        if project:
            Update_Module_Setting(id=module.id, project_id=project.id)
            print("update one module's project_id, continue...")
    return True

def baseModel_delete_test():
    module = Module.query.first()
    module.delete()
    if module.is_deleted == 0:
        print 'fail delete'


def string_validate():
    usernames = {'中dd文':'@^$*#%(*','325325':'32958','user_':'pas_','us-er':'pasdddddd','udfajgjadjgflajglajflk':'jf32978@dlgj    fm','df&32':'0'}
    for k,v in usernames.items():
        if Is_Username_Validate(k):
            print 'username valid',k
        else:
            print 'username invalid',k

        if Is_Password_Validate(v):
            print 'password valid',v
        else:
            print 'password invalid',v

def set_recommend_projects_random():
    vip_user = User.query.filter_by(username="russell-vip-test").first()
    projects = Project.query.filter_by(owner_id=vip_user.id if vip_user else '').all()
    for project in projects:
        project.is_recommended = True
        db.session.commit()
def set_recommend_data_random():
    datas = Data.query.all()
    for data in datas:
        data.is_recommended = True
        db.session.commit()
        print 'recommend', data.id

if __name__ == '__main__':
    set_recommend_data_random()
    # set_recommend_projects_random()
    # create_all_images()
    # fill_experiments_project_id()
    # fill_modules_project_id()
    # fill_data_image()
    # fill_profiles()
    # fill_projects()