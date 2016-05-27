# coding:utf-8

import copy

head = {}
nxt = []
to = []
tot = 0
edge = set()
#vis = set()
allpath = []
nowpath = []

def init():
    global head,nxt,to,tot,edge,vis,allpath
    
    head = {}
    nxt = []
    to = []
    tot = 0
    edge = set()
    vis = set()
    allpath = []
    

def AddOne(a, b):
    global head,nxt,to,tot,edge,vis,allpath
    
    if (a,b) in edge:
        return
    edge.add((a,b))
    to.append(b)
    if head.has_key(a):
        nxt.append(head[a])
    else:
        nxt.append(-1)
    head[a]=tot
    tot += 1
    
def AddTwo(a, b):
    AddOne(a, b)
    AddOne(b, a)
    
def DFS(a, b, cnt):
    global head,nxt,to,tot,edge,vis,allpath

    if a==b:
        allpath.append(copy.deepcopy(nowpath))
    if cnt == 3:
        return
    if head.has_key(a):
        v = head[a]
        while v>=0:
            if to[v] not in vis:
#                vis.add(to[v])
                nowpath.append(to[v])
                DFS(to[v],b,cnt+1)
                nowpath.pop()
#               vis.remove(to[v])
            v=nxt[v]
    
def FindPath(a, b):
    global head,nxt,to,tot,edge,vis,allpath
    
#    vis.add(a)
    nowpath.append(a);
    DFS(a, b, 0)
    nowpath.pop()
#    vis.remove(a)
