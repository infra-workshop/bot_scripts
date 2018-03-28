#!/usr/bin/python3
# vim: set fileencoding=utf-8 :

# require `pip3 install twitter`
# require `export PYTHONIOENCODING=utf-8`

import twitter
import sys
import os

import configparser
import codecs

import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG = True

CONSUMER_KEY = None
CONSUMER_SECRET = None
TOKEN = None
TOKEN_SECRET = None

def log(msg):
    if DEBUG:
        f = open(BASE_DIR + "/run.log","a")
        f.write(str(msg) + "\n")
        f.close()

def post(word):
    auth = twitter.OAuth(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        token=TOKEN,
        token_secret=TOKEN_SECRET)
    t = twitter.Twitter(auth=auth)
    word = word.replace('\\n',"\n")
    log(word)
    ret = t.statuses.update(status=word)
    log(ret)

if __name__ == '__main__':
    # Get Credential Key
    try:
        parser = configparser.ConfigParser()
        parser.readfp(codecs.open(BASE_DIR + '/config.ini', "r", "utf8"))
        CONSUMER_KEY = parser['twitter-key']['consumer_key']
        CONSUMER_SECRET = parser['twitter-key']['consumer_secret']
        TOKEN = parser['twitter-key']['token']
        TOKEN_SECRET = parser['twitter-key']['token_secret']
    except:
        log("Failed while parsing config")
        log(traceback.format_exc())
        exit(-1)

    # Create PostMessage from args
    argvs = sys.argv
    argc = len(argvs)
    if argc < 2:
        log("No Message")
        exit(-1)
    argvs.pop(0)
    argw = ""
    for argv in argvs:
       argw = argw + " " +  argv
    post(argw)
