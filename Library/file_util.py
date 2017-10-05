import os
##################     文件相关      ##################
def concat_dirs(is_abs=False,*dirs):
    '''
    将多级目录连接起来，os.path.join()的迭代版本, 可用..表示上层目录
    :param dirs:
    :return:
    '''
    joined_path = ''
    for dir in dirs:
        if dir != '..':
            joined_path = os.path.join(joined_path,dir)
        elif dir == '..':
            joined_path = os.path.dirname(joined_path)
    if joined_path.endswith(('/','\\')):
        joined_path = joined_path[:-1]
    return os.path.abspath(joined_path) if is_abs else joined_path
##################     文件相关      ##################

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil
import os


def copy_dir(source, target):
    if os.path.exists(source):
        shutil.copytree(source, target)
        return True
    else:
        return False


def save_dir(file_list,target):
    os.mkdir(target)
    for file in file_list:
        if allowed_file(file.filename):
            file_name = file.filename
            path = os.path.dirname(file_name)
            path = os.path.join(target, path)
            if not os.path.exists(path):
                os.makedirs(path)
            file_path = os.path.join(target, file_name)
            file.save(file_path)
    return

def read_file(file_path):
    if os.path.isfile(file_path):
        with open(file_path, "r") as myfile:
            data = myfile.read()
        return data
    return None

def write_file(log_str, file_path):
    if not os.path.exists(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))
    with open(file_path, "a") as myfile:
        myfile.write(log_str)

def allowed_file(filename):
    return True
    # return '.' in filename and filename.rsplit('.', 1)[1] in flask_app.config['ALLOWED_EXTENSIONS']


def estimate_copy_time(path, default_speed=100):
    '''

    :param path:
    :param default_speed: copy speed MB/s
    :return:
    '''
    if os.path.isdir(path):
        size = 0    # BYTES
        for root, dirs, files in os.walk(path):
            size += sum([os.path.getsize(os.path.join(root, name)) for name in files])

    elif os.path.isfile(path):
        size = os.path.getsize(path)
    else:
        size = 0
    return size / default_speed / (1<<20)

def Get_Dir_Filelist_Deeply(dir_path, ignores=None, only=None):
    if not os.path.isdir(dir_path):
        return None
    filenames = os.listdir(dir_path)
    os.chdir(dir_path)
    filtered_files = []
    for filename in filenames:
        if os.path.isdir(filename):
            subdir_filenames = Get_Dir_Filelist(filename, ignores, only)
            for subdir_filename in subdir_filenames:
                filtered_files.append(os.path.join(filename, subdir_filename))
        elif os.path.isfile(filename):
            filtered_files += Get_Dir_Filelist(filename, ignores, only)
    return filtered_files


def Get_Dir_Filelist(dir_path, ignores=None, only=None):
    '''

    :param dir_path: file is elso ok
    :param ignore: []
    :param only: {'endswith','in','startswith'...}
    :return:
    '''
    if not os.path.isdir(dir_path):
        filenames = [dir_path] if os.path.isfile(dir_path) else []
    else:
        filenames = os.listdir(dir_path)
    filtered_files = []
    if only is not None and isinstance(only, dict) and ignores is None:
        # TODO
        filtered_files = [filename for filename in filenames if filename.endswith(only.get('endswith', ''))]
    elif ignores is not None:
        for filename in filenames:
            for ignore in ignores:
                # TODO 正则
                if ignore not in filename:
                    filtered_files.append(filename)
    else:
        filtered_files = filenames
    return filtered_files