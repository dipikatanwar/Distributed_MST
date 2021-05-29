import threading
from Node import Node
from constants import *
import random
import math

class UnionFind():
    def __init__(self, N):
        self.A = [i for i in range(N)]
        self.sz = [1 for i in range(N)]
        self.size = N

    def root(self, u):
        while self.A[u] != u:
            self.A[u] = self.A[self.A[u]]
            u = self.A[u]
        return u 

    def find(self, u, v):
        return self.root(u) == self.root(v)

    def union(self, u, v):
        p = self.root(u)
        q = self.root(v)
        if p==q: return False
        if self.sz[p] > self.sz[q]:
            self.A[q] = p
            self.sz[p] += self.sz[q]
        else:
            self.A[p] = q
            self.sz[q] += self.sz[p]

    def getSize(self, p):
        return self.sz[p]
 


class Graph():
    @staticmethod
    def createGraphFromInput_mat(inputFile):
        lines = open(inputFile, 'r').readlines()
        N,E,graph = None,0, None
        for line in lines:
            line = line.strip()
            if N == None:
                N = int(line)
                graph = [[None for i in range(N)] for j in range(N)]
            else:
                u,v,w = (line[1:-1]).split(',')
                u,v,w = int(u),int(v),int(w)
                graph[u][v] = graph[v][u] = w
                E += 1
        return N,E,graph

    @staticmethod
    def createGraphFromInput_list(inputFile):
        lines = open(inputFile, 'r').readlines()
        N, graph, E = None, None, 0
        for line in lines:
            line = line.strip()
            if N == None:
                N = int(line)
                graph = {i:[] for i in range(N)}
            else:
                u,v,w = (line[1:-1]).split(',')
                u,v,w = int(u),int(v),int(w)
                graph[u].append((v,w))
                graph[v].append((u,w))
                E += 1
        for i in range(N):
            graph[i] = sorted(graph[i],key = lambda x: x[1])
        return N,E,graph

    @staticmethod
    def createRandomGraph_mat(N, density):
        weights = [x for x in range(1, 160001)][:N*N]
        random.shuffle(weights)
        graph = [[None for i in range(N)] for j in range(N)]
        E, weight = 0, 0
        for i in range(N):
            for j in range(i+1, N):
                if density >= random.random():
                    graph[i][j] = graph[j][i] = weights[weight]
                    E += 1
                    weight += 1
        return N, E, graph


    @staticmethod
    def createRandomGraph_list(N, density):
        weights = [x for x in range(1, 160001)][:N*N]
        random.shuffle(weights)
        graph = {i:[] for i in range(N)}
        E, weight = 0, 0
        uf = UnionFind(N)
        for i in range(N):
            for j in range(i+1, N):
                if density >= random.random():
                    graph[i].append((j,weights[weight]))
                    graph[j].append((i,weights[weight]))
                    weight += 1
                    E += 1
                    uf.union(i,j)
        
        for i in range(N):
            for j in range(i+1, N):
                if uf.find(i,j) == False:
                    graph[i].append((j,weights[weight]))
                    graph[j].append((i,weights[weight]))
                    uf.union(i,j)
                    weight += 1
                    E += 1

        for i in range(N):
            graph[i] = sorted(graph[i],key = lambda x: x[1])
        return N, E, graph

    @staticmethod
    def mstTotalMessageSent():
        totalMessage = 0
        for node in nodeInfo.values():
            totalMessage += node.messageCount
        return totalMessage
    
    @staticmethod
    def mstTotalMessageGHSLimit(E, N):
        return 2*E + 5*N*math.log(N,2)


    @staticmethod
    def createMST(N, graph):
        threadPool = []
        nodeInfo.clear()
        output.clear()
        FLG.STOP = False
        for nodeId in range(N):
            node = Node(N, nodeId, graph[nodeId])
            nodeInfo[nodeId] = node

        for node in nodeInfo.values():
            t = threading.Thread(target=node.work, args=[], daemon=True)
            t.start()
            threadPool.append((t, nodeId))
        for t, nodeId in threadPool:t.join()

    @staticmethod
    def writeMSTToFile(outFile):
        for node in nodeInfo.values():
            for n,w in node.nbrList:
                if w not in output.keys() and node.status[n] == BRANCH:
                    if node.nodeId < n:
                        output[w] = (node.nodeId, n, w)
                    else:
                        output[w] = (n, node.nodeId, w)

        data = sorted(output.values(), key=lambda e:e[2])
        with open(outFile, "w") as fp:
            for e in data:
                fp.write('(' +str(e[0])+ ' , ' + str(e[1]) + ', ' + str(e[2]) +')\n')
