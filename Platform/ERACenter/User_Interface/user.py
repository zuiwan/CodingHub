#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:       user
   Description:
   Author:          huangzhen
   date:            2018/3/13
-------------------------------------------------
   Change Activity:
                   2018/3/13:
-------------------------------------------------
The makeReservation method

The interface with the user reservation requests is composed of the single “makeReservation” method, which handles a job reservation request that is sent by some user. Each reservation request can either be accepted and priced or declined by ERA.
The basic input parameters to this method are the job’s bid and the identifier of the job. The bid encapsulates a list of resource requests along with the maximum price that the user is willing to pay in order to get this request (as described above). The output is an acceptance or rejection of the request, and the price that the user will be charged for fulfilling his request in case of acceptance.（Alternatively, the system may allow determining the payment after running is completed (depending on the system load at that time), or may allow flexible payments that take into account boththe amount of resources reserved and the amount of resources actually used.）

The main effect of accepting a job request is that the user is guaranteed to be given the desired amount of resources sometime within the desired time window. An accepted job must be ready to use all requested resources starting at the beginning of the requested window, and the request is considered fulfilled as long as ERA provides the requested resources within the time window.
"""
__author__ = 'huangzhen'


'''


'''

def makeReservation(request):
    pass