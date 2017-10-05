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