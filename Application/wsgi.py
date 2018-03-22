#!/usr/in/env python
# -*- coding: utf-8 -*-
from Application.api import flask_app

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', debug=True)
