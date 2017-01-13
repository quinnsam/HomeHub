#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import os
import datetime
import hashlib

from OpenSSL import SSL
from flask import Flask, jsonify, request


# Load config file
#------------------------------------------------------------------------------#
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
try:
    with open(os.path.join(__location__, 'HomeHUB.json')) as data_file:
        config = json.load(data_file)
except:
    print 'ERROR: Could not load configuration file %s' % os.path.join(__location__, 'HomeHUB.json')
    sys.exit(1)

def log(msg, pri):
    temp = ''
    time = datetime.datetime.now()

    if config['logfile']:
        logfile = config['logfile']
    else:
        print '%s:%s' % (pri,msg)
        return 1

    if pri == 0:
        temp = '[info]\t%s - %s' % (time,msg)
    elif pri == 1:
        temp = '[error]\t%s - %s' % (time,msg)
    elif pri == 2:
        temp = '[warn]\t%s - %s' % (time,msg)
    else:
        temp = '[%s]\t%s - %s' % (pri,time, msg)

    with open(logfile, 'a') as logf:
        logf.write('%s\n' % temp)

    print temp
    return 0


def process_file(file_name):

    user_names = []
    passwords = []

    try:
        file_conn = open(file_name)
        data = file_conn.readlines()

        for i in range(len(data)):
            if i%2 == 0:
                user_names.append(data[i][:-1])
            else:
                passwords.append(data[i][:-1])

        file_conn.close()
    except:
        return "", ""
    return user_names, passwords


def push_notify(x):
    config = get_config()
    if not config: return 1
    pb = Pushbullet(config['pushbullet-api'])
    if not pb.push_note('Autodoor',x):
        print 'Error in PushBullet message'
        return 1
    return 0



def auth_user(user, password):

    passwd_file = config['passwd_file']
    if not os.path.isfile(passwd_file):
        log("PASSWD file not found at: %s" % passwd_file, 1)
        return -4

    user_names, passwords = process_file(passwd_file)

    if user not in user_names:
        return -1

    user_input = hashlib.sha224(password).hexdigest()
    if user_input != passwords[user_names.index(user)]:
        print 'Incorrect Password'
        return -2
    else:
        print 'User Authenticated\n'
        return 1

    return -3

def light_action(act):
    if act == 'all':
        log('All Lights ON', 0)
    elif act == 50:
        log('Lights 50%', 0)
    elif act == 'off':
        log('All Lights OFF', 0)

def api_server():
    if config['https'] == 'True':
        log('HTTPS enabled', 0)
        context = SSL.Context(SSL.SSLv23_METHOD)
        if os.path.isfile(config['sslcrt']):
            crt = config['sslcrt']
            log('SSL crt is set to %s' % crt, 0)
        if os.path.isfile(config['sslkey']):
            key = config['sslkey']
            log('SSL key is set to %s' % key, 0)

    if config['apikey']:
        apikey = '%s' % config['apikey']
        log('API key set to %s' % apikey, 0)
        route = '/homehub/%s' % apikey
    else:
        apikey = ''
        log('NO API key set, continuing unsecurely', 2)
        route = '/homehub'

    log('API Server is located at <IP ADRESS>%s/' % route, 0)




    app = Flask(__name__)
    @app.route('%s/lights/' % (route), methods=['POST'])
    def lights():
        if request.headers['content-Type'] == 'application/json':
            data = request.json
            action = data['action']
            if config['use_secure'] == 'True':
                # Get username and Password form POST and check against passwd file.
                user = data['user']
                passwd = data['passwd']
                auth = auth_user(user,passwd)
            else:
                # No user name or password always authenticate
                auth = 1
                user = 'UNKNOWN'

            # User Authenticated
            if auth == 1:
                log('User Authenticated: %s , Action: %s' % (user, action), 0)
		light_action(action)
                return jsonify('{ "User" : "%s", "Action" : "%s", "Response" : "True" }' % (user,action))
            elif auth == -2:
                log('Invalid Password for %s' % user, 2)
                return jsonify('{ "User" : "%s", "Action" : "%s", "Response" : "Invalid Password" }' % (user,action))
            elif auth == -1:
                log('Invalid Username %s' % user, 2)
                return jsonify('{ "User" : "%s", "Action" : "%s", "Response" : "Invalid Username" }' % (user,action))
            else:
                log('Unknown ERROR in Auth%s', 1)
                return jsonify('{ "User" : "%s", "Action" : "%s", "Response" : "Unknown ERROR" }' % (user,action))
        else:
            return '415 Unsupported Media Type'


    if config['https'] == 'True':
        context = (crt,key)
        app.run(host='0.0.0.0', ssl_context=context)
    else:
        app.run(host='0.0.0.0')









api_server()
