import os
import sys
import configparser

ROOT_PATH = './etc'
CONFIG_FILE_PATH = os.path.join(ROOT_PATH, 'hippools.conf')

config = configparser.ConfigParser()

if not config.read(CONFIG_FILE_PATH):
    print("Cannot find hippools configurstion file %s" % CONFIG_FILE_PATH)
    sys.exit(1)

try:
    DB_PATH = config['HIPPOOLSD']['DBPath'].strip()
    LOGLEVEL = config['HIPPOOLSD']['LogLevel'].strip()
    LOGFILE = config['HIPPOOLSD']['LogFile'].strip()
    ALL_IP_POOLS = {}

    for pool_name, pool in config['HIPPOOLS'].items():
        ALL_IP_POOLS.update({pool_name.strip(): [p.strip() for p in pool.split(',')]})

    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)

except Exception as e:
    print ("Invalid config parameter. (%s)" % e)
    sys.exit(1)
