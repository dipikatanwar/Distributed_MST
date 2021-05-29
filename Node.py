import threading
from constants import *
import math
from time import sleep,time
from collections import deque

MAX = 9999999

class Node():
    def __init__(self,totalNode, nodeId, nbrList):
        self.nodeId,self.totalNode = nodeId,totalNode
        self.nbrList = nbrList.copy()
        self.nbrDict = {}
        for n,w in self.nbrList: self.nbrDict[n] = w
        self.receiveQueue = deque()
        self.threadLock = threading.Lock()
        self.threadStopLock = threading.Lock()
        self.messageCount = 0

    def writeToLog(self,logline):
        f = open('logs\\' + str(self.nodeId) + '.txt', 'a+')
        f.write(logline)
        f.close()

    def receive(self):
        ret = True
        self.threadLock.acquire()
        try:
            type1, data = self.receiveQueue.popleft()
        except Exception as _:
            ret,type1,data = False, None, None
        self.threadLock.release()
        return ret, type1, data


    def sendMessage(self, type1, dest, data):
        dest.threadLock.acquire()
        dest.receiveQueue.append((type1,data))
        dest.threadLock.release()
        # self.messageCount += 1
        if dest != self:
            self.messageCount += 1

    def recv_test(self, data):
        q,leveld, named = data['sender'],data['level'], data['name']
        if leveld > self.level:
            sendData = data.copy()
            sendData['repeat'] = True
            sleep(0.01)
            self.sendMessage(MSG.TEST,self,data.copy())
        elif self.name == named:
            if self.status[q.nodeId] == BASIC:
                self.status[q.nodeId] = REJECT
            if q != self.testNode:
                sendData = {}
                sendData['sender'] = self
                self.sendMessage(MSG.REJECT, q,sendData)
            else:
                self.findMin()
        else:
            sendData = {}
            sendData['sender'] = self
            self.sendMessage(MSG.ACCEPT, q , sendData)

    def recv_accept(self,data):
        q = data['sender']
        self.testNode = None
        wpq =  self.nbrDict[q.nodeId]
        if wpq < self.bestWt:
            self.bestWt = wpq
            self.bestNode = q
        self.report()

    def recv_reject(self,data):
        q = data['sender']
        if self.status[q.nodeId] == BASIC:
            self.status[q.nodeId] = REJECT
        self.findMin()

    def recv_report(self,data):
        q, w = data['sender'], data['bestWt']
        if q!= self.parent:
            if w < self.bestWt:
                self.bestWt = w
                self.bestNode = q
            self.rec += 1
            self.report()
        else:
            if self.state == FIND:
                # sleep(0.1)
                sendData = data.copy()
                sendData['repeat'] = True
                sleep(0.01)
                self.sendMessage(MSG.REPORT,self,sendData)
            elif w > self.bestWt:
                self.changeRoot()
            elif w == MAX and self.bestWt == MAX:
                self.stopAll()

    def recv_connect(self, data):
        q, L = data['sender'], data['level']
        if L < self.level:
            self.status[q.nodeId] = BRANCH      
            sendData = {}
            sendData['sender'], sendData['level'], sendData['name'], sendData['state'] = self,self.level, self.name, self.state
            self.sendMessage(MSG.INITIATE, q, sendData)
        elif self.status[q.nodeId] == BASIC:
            sendData = data.copy()
            sendData['repeat'] = True
            sleep(0.01)
            self.sendMessage(MSG.CONNECT, self, data.copy())
        else:
            sendData = {}
            sendData['sender'], sendData['level'], sendData['name'], sendData['state'] = self, self.level + 1,self.nbrDict[q.nodeId], FIND
            self.sendMessage(MSG.INITIATE, q, sendData)

    def recv_initialte(self, data):
        q, leveld, named, stated = data['sender'], data['level'],data['name'], data['state']
        self.parent, self.level, self.name, self.state = q, leveld, named, stated
        self.bestNode, self.testNode, self.bestWt= None, None, MAX
        self.status[q.nodeId] = BRANCH    

        for r, _ in self.nbrList:
            if self.status[r] == BRANCH and r != q.nodeId:
                sendData = {}
                sendData['sender'], sendData['level'],sendData['name'], sendData['state'] = self, leveld,named,stated
                self.sendMessage(MSG.INITIATE,nodeInfo[r],sendData)
        if stated == FIND:
            self.rec = 0
            self.findMin()
    
    def recv_changeRoot(self):
        self.changeRoot()


    def initialize(self):
        self.status = {}
        for n, _ in self.nbrList: self.status[n] = BASIC

        self.parent = None
        bNbr, _ = self.nbrList[0]
        self.name,self.status[bNbr],self.level,self.state,self.rec = 0,BRANCH,0,FOUND,0

        bNbr = nodeInfo[bNbr]
        sendData = {}
        sendData['sender'] = self
        sendData['level'] = self.level
        self.sendMessage(MSG.CONNECT, bNbr, sendData)

    def findMin(self):
        bNbr = None
        for n, _ in self.nbrList:
            if self.status[n] == BASIC:
                bNbr = n
                break
        if bNbr != None:
            self.testNode = nodeInfo[bNbr]
            sendData = {}
            sendData['sender'] = self
            sendData['level'] = self.level
            sendData['name'] = self.name
            self.sendMessage(MSG.TEST,self.testNode, sendData)
        else:
            self.testNode = None
            self.report()

    def report(self):
        count = 0
        for n,_ in self.nbrList:
            if self.status[n] == BRANCH and n != self.parent.nodeId:
                count += 1
        if(count == self.rec and self.testNode == None):
            self.state = FOUND
            sendData = {}
            sendData['sender'], sendData['bestWt'] = self, self.bestWt
            self.sendMessage(MSG.REPORT, self.parent, sendData)

    def changeRoot(self):
        if self.status[self.bestNode.nodeId] == BRANCH:
            sendData = {}
            sendData['sender'] = self
            self.sendMessage(MSG.CHNAGE_ROOT, self.bestNode,sendData)
        else:
            self.status[self.bestNode.nodeId] = BRANCH
            sendData = {}
            sendData['sender'], sendData['level'] = self, self.level
            self.sendMessage(MSG.CONNECT, self.bestNode,sendData)
        
    def isRunning(self):
        writeToMAP.acquire()
        finishTask = FLG.STOP
        writeToMAP.release()
        return finishTask
    
    def stopAll(self):
        writeToMAP.acquire()
        FLG.STOP = True
        writeToMAP.release()

    def work(self):
        self.initialize()
        while False == self.isRunning():
            ret, type1,data = self.receive()
            if ret == False:continue
            if type1 == MSG.CONNECT:
                self.recv_connect(data)
            elif type1 == MSG.INITIATE:
                self.recv_initialte(data)
            elif type1 == MSG.TEST:
                self.recv_test(data)
            elif type1 == MSG.ACCEPT:
                self.recv_accept(data)
            elif type1 == MSG.REJECT:
                self.recv_reject(data)
            elif type1 == MSG.REPORT:
                self.recv_report(data)
            elif type1 == MSG.CHNAGE_ROOT:
                self.recv_changeRoot()
            else:break
