# -*- coding: utf-8 -*-
import time
import traceback
import os
import logging
import logging.config
from functools import wraps

from Application.app import flask_app
from logging.handlers import RotatingFileHandler

from Library.Utils.func_util import Is_Cls
from Library.singleton import (
    ThreadSafeSingleton,
    Singleton
)
import sys


def check_api_cost_time(method):
    @wraps(method)
    def _decorator(*args, **kwargs):
        try:
            start = time.time()
            ret = method(*args, **kwargs)
            end = time.time()
            # print(method.__name__ + " api cost time %f s" % (end - start))
            file_name = method.func_code.co_filename
            line_num = method.func_code.co_firstlineno
            if args is not None and len(args) > 0 and Is_Cls(args[0]):
                # 类（实例）方法
                name = "Function: {function_name}, @Class: {class_name}, @File: {file_name}, @Line: {line_num}" \
                    .format(function_name=method.__name__,
                            class_name=args[0].__class__.__name__,
                            file_name=file_name,
                            line_num=line_num)
            else:
                name = "Function: {function_name}, @File: {file_name}" \
                    .format(function_name=method.__name__,
                            file_name=file_name,
                            line_num=line_num)
            global_loggers.debug(name + " api cost time %f s" % (end - start))
            return ret
        except Exception as e:
            global_loggers.error(repr(traceback.format_exc()))

    return _decorator


def Celery_Log_Line(log_str, level="INFO"):
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    current_time = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
    line = "[{}] [{}] | {}\n".format(current_time, level, log_str)
    return line


@ThreadSafeSingleton
class LogCenter(object):
    def __init__(self):
        self.logger_map = {}

    def get_logger(self, name, filename=None):
        """ return logger"""
        if filename is None:
            filename = name
        logger_name = '_'.join((name, filename))
        if not logger_name in self.logger_map:
            self.logger_map[logger_name] = MyLogger(name, filename)
        return self.logger_map[logger_name]


output_log_basepath = flask_app.config['APP_LOG_FOLDER']


class MyLogger():
    def __init__(self, name, filename=None):
        if filename is None:
            filename = name
        self.logger = self._get_logger(name, filename)

    def debug(self, message):
        global_loggers.debug(message)
        self.logger.debug(message)

    def info(self, message):
        global_loggers.info(message)
        self.logger.info(message)

    def warning(self, message):
        global_loggers.warning(message)
        self.logger.warning(message)

    def error(self, message):
        global_loggers.error(message)
        self.logger.error(repr(traceback.format_exc()))
        self.logger.error(message)

    def _get_logger(self, logger_file, file):
        dir_path = '%s%s' % (output_log_basepath, logger_file)
        self._mkdir(dir_path)

        logger = logging.getLogger(logger_file)

        # 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s]: %(filename)s[line:%(lineno)d] [pid:%(process)d] %(levelname)s %(message)s")
        console.setFormatter(formatter)
        logger.addHandler(console)

        # 定义一个RotatingFileHandler，最多备份5个日志文件，每个日志文件最大5M
        Rthandler = RotatingFileHandler('%s/%s.log' % (dir_path, file), maxBytes=5 * 1024 * 1024, backupCount=10)
        Rthandler.setLevel(logging.DEBUG)
        Rformatter = logging.Formatter(
            "[%(asctime)s]: %(filename)s[line:%(lineno)d] [pid:%(process)d] %(levelname)s %(message)s")
        Rthandler.setFormatter(Rformatter)
        logger.addHandler(Rthandler)

        logger.setLevel(logging.DEBUG)
        return logger

    def _mkdir(self, path):
        # 去除首位空格
        path = path.strip()
        # 去除尾部 \ 符号
        path = path.rstrip("\\")

        # 判断路径是否存在
        # 存在     True
        # 不存在   False
        isExists = os.path.exists(path)

        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(path)
            return True
        else:
            return False

    def get_this_exception_info(self):
        '''获取当前异常出现的信息
        输出: result={'type':exc_type,'value':exc_value,'tb':exc_tb,'line_number':exc_tb.lineno}
            type：异常类型  value：异常值    tb:异常信息   line_number:异常行数'''
        exc_type, exc_value, exc_tb = sys.exc_info()
        result = {}
        result['type'] = exc_type
        result['value'] = exc_value
        result['exc_tb'] = exc_tb
        result['line_number'] = exc_tb.tb_lineno
        return result

    def get_exception_lineno(self):
        '''取出异常行数
        '''
        return self.get_this_exception_info()['line_number']


global_loggers = MyLogger('GlobalLog').logger
