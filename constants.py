import threading
nodeInfo = {}


SLEEP = 0
FIND = 1
FOUND = 2

BASIC = 0
BRANCH = 1
REJECT = 2

class FLG():
    STOP = False

class MSG():
    CONNECT = 0
    INITIATE = 1
    TEST = 2
    ACCEPT = 3
    REJECT = 4
    REPORT = 5
    CHNAGE_ROOT = 6

messageType = [MSG.CONNECT, MSG.INITIATE, MSG.TEST, MSG.ACCEPT, MSG.REJECT, MSG.REPORT, MSG.CHNAGE_ROOT]


output = {}
writeToMAP = threading.Lock()

# LOG = True
LOG = False
