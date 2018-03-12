# coding: utf-8
import requests
import sys
import time
import traceback
import os
import json
import tarfile
import zipfile
from functools import wraps
from flask import request
from functools import update_wrapper
from flask import Response, current_app
import time
import traceback
import logging

default_access_token = {"username": "huangzhen",
                "token": "ZXlKaGJHY2lPaUpJVXpJMU5pSXNJbVY0Y0NJNk1UVXdOak0wTVRBeE15d2lhV0YwSWpveE5UQTJNekExTURFemZRLmV5SnBaQ0k2SWpNMVl6YzVORGMxTTJVNU5qUXdORGM0TXpaak1qWmlPV1V6WTJNME9XVTBJbjAuam1DaTN2bVFYZmxDdzJ2eDRUSk9Nc3JlOEx3em5Hc19EQTBfVGhNRmxiczo=",
                "expiry": None}

access_token_vip = {"username": "russell-vip-test",
                    "token": "Basic cnVzc2VsbC12aXAtdGVzdDpydXNzZWxsLXZpcC10ZXN0",
                    "expiry": None}

access_token_1 = {"username": "",
                  "token": "",
                  "expiry": None}

access_tokens = (default_access_token, access_token_vip, access_token_1)

def Print_Response(method):
    @wraps(method)
    def _decorator(*args, **kwargs):
        test_logger.info('-' * 80)
        start_at = time.time()
        test_logger.info('#'*3 + " Request Start at " + str(start_at) + ' ' + '#'*3)
        test_logger.info('#'*3 + " Request args Start " + '#'*3)
        for kwarg in kwargs:
            test_logger.info(kwarg.__str__() + " : " + kwargs.get(kwarg).__str__())
        test_logger.info('#'*3 + "  Request args End " + '#'*3)
        try:
            resp = method(*args, **kwargs)
        except Exception as e:
            test_logger.error(repr(traceback.format_exc()))
            return
        end_at = time.time()
        test_logger.info('#'*3 + " Request End at " + str(end_at) + ", cost " + str(end_at-start_at) + " s " + '#'*3)
        if not isinstance(resp, unicode) and not isinstance(resp, str):
            if isinstance(resp, dict):
                for k in resp:
                    if isinstance(resp[k], dict):
                        value = resp[k].__str__()
                    else:
                        value = str(resp[k]).decode('utf-8')
                    test_logger.info(k.decode('utf-8') + " : " + value)
            else:
                test_logger.error(type(resp) + resp.__str__() + repr(traceback.format_exc()))
        else:
            try:
                test_logger.info(resp)
            except:
                test_logger.info(repr(traceback.format_exc()))
        test_logger.info('-'*80)
        return resp
    return _decorator

class REST_API_Test(object):
    def __init__(self):
        self.base_url = "http://test.dl.russellcloud.com"
        self.access_token = default_access_token
        self.db = Test_Data_Manager()

    def __run__(self):
        self.get()
        self.put()
        self.post()
        self.delete()

    def get(self):
        pass

    def put(self):
        pass

    def post(self):
        pass

    def delete(self):
        pass

    @Print_Response
    def request(self,
                method,
                url,
                params=None,
                data=None,
                files=None,
                timeout=5,
                access_token=None,
                stream=False):
        # type: (str, str, dict, dict, object, int, str, bool) -> object
        """
        Execute the request using requests library
        """
        request_url = self.base_url + url
        test_logger.debug(
            "Starting request to url: {} with params: {}, data: {}".format(request_url, params, data))
        if access_token:
            headers = {"Authorization": "Basic {}".format(access_token)}
        else:
            headers = {"Authorization": "Basic {}".format(
                self.access_token.get('token') if self.access_token else None)
            }

        try:
            # print "url: {}".format(request_url)
            # print "params: {}".format(params)
            # print "data: {}".format(data)
            response = requests.request(method,
                                        request_url,
                                        params=params,
                                        headers=headers,
                                        data=data,
                                        files=files,
                                        timeout=timeout,
                                        stream=stream)
        except requests.exceptions.ConnectionError:
            sys.exit("Cannot connect to the Russell server. Check your internet connection.")

        if not stream:
            try:
                test_logger.debug(
                    "Response Content: {}, Headers: {}".format(response.json(), response.headers))
            except Exception:
                test_logger.debug("Request failed. Response: {}".format(response.content))
            self.check_response_status(response)
            return response.json().get("data", "")
        else:
            test_logger.info('HTTP Stream Request/Response...')
            self.check_response_status(response)
            return response

    def check_response_status(self, response):
        """
        Check if response is successful. Else raise Exception.
        """
        if not response.headers.get('Content-Type') == 'application/json':
            return
        if not (200 <= response.status_code < 300 and response.json() is not None and response.json().get("code") != None):
            if response.status_code == 401:
                test_logger.info("AuthenticationException")
            elif response.status_code == 401:
                test_logger.info("NotFoundException")
            elif response.status_code == 500:
                test_logger.error("服务器错误")
                sys.exit("服务器错误， 测试中止")
            else:
                test_logger.info("InvalidResponseException")
                test_logger.error("服务器响应异常， 测试中止")
                sys.exit("服务器响应异常， 测试中止")

        code = response.json().get("code")
        if not (200 <= code < 300):
            try:
                message = response.json().get("data", "").encode('utf-8')
            except Exception:
                message = None
            test_logger.debug("Error received : status_code: {}, message: {}".format(code,
                                                                          message or response.content))
            if code == 517:
                test_logger.error("NotFoundException")
            elif code == 512:
                test_logger.error("AuthenticationException")
            elif code == 519:
                test_logger.error("BadRequestException")
            elif code == 518:
                test_logger.error("NoRequestException")
            elif code == 520:
                test_logger.error("OverLimitException")
            elif code == 522:
                # raise OverPermissionException()
                test_logger.error("OverPermissionException")
            else:
                response.raise_for_status()

    def download(self, url, filename, timeout=10):
        """
        Download the file from the given url at the current path
        """
        test_logger.debug("Downloading file from url: {}".format(url))

        try:
            # response = requests.get(request_url,
            #                         headers=request_headers,
            #                         timeout=timeout,
            #                         stream=True)
            response = self.request(method='GET',
                                    url=url,
                                    stream=True,
                                    timeout=timeout
                                    )
            self.check_response_status(response)
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return filename
        except requests.exceptions.ConnectionError as exception:
            test_logger.debug("Exception: {}".format(exception))
            sys.exit("Cannot connect to the Russell server. Check your internet connection.")

    def download_compressed(self, url, compression='tar', uncompress=True, delete_after_uncompress=False,
                            dir=None):
        """
        Download and optionally uncompress the tar file from the given url
        """
        if dir:
            if os.path.exists(dir):
                test_logger.info("ExistedException")
            else:
                os.mkdir(dir)
                os.chdir(dir)
        try:
            test_logger.info("Downloading the tar file to the current directory ...")
            filename = self.download(url=url, filename='output')
            if filename and os.path.isfile(filename) and uncompress:
                test_logger.info("uncompressring the contents of the file ...")
                if compression == 'tar':
                    tar = tarfile.open(filename)
                    tar.extractall()
                    tar.close()
                elif compression == 'zip':
                    zip = zipfile.ZipFile(filename)
                    zip.extractall()
                    zip.close()
            if delete_after_uncompress:
                test_logger.info("Cleaning up the compressed file ...")
                os.remove(filename)
            return filename
        except requests.exceptions.ConnectionError as e:
            test_logger.info("Download ERROR! {}".format(e))
            return False