#!/usr/in/env python
# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 把项目目录加载到$PYTHONPATH中

from Application.api import flask_app

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', debug=True)
