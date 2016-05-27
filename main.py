# coding: utf-8

import data
import json
import requests
import threading
import time

prefix = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr='
suffix = '&model=latest&count=10000&offset=%d&attributes=Id,AA.AuId,AA.AfId,J.JId,C.CId,F.FId,RId,CC&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'
onlyId = '&model=latest&count=10000&offset=%d&attributes=Id,AA.AuId,AA.AfId,J.JId,C.CId,F.FId&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'
USE_MULTI_THREAD = True

class MultiGet(threading.Thread):
    def __init__(self, id, cls, ofs = 0):
        threading.Thread.__init__(self)
        self.id = id
        self.cls = cls
        self.ofs = ofs
        self.d = []
    def run(self):
        self.d = GetData(self.id, self.cls, self.ofs)
        if self.cls == 2:
            for i in self.d:
                if i.has_key('Id'):
                    data.AddOne(i['Id'],self.id)


def AddEdge(d):
    for i in d:
        if not i.has_key('Id'):
            continue
        id = i['Id']
        # add RId
        if i.has_key('RId'):
            for j in i['RId']:
                data.AddOne(id,j)
                
        # add AuId AfId
        if i.has_key('AA'):
            for j in i['AA']:
                if j.has_key('AuId'):
                    data.AddTwo(id,j['AuId'])
                    if j.has_key('AfId'):
                        data.AddTwo(j['AuId'],j['AfId'])
                        
        # add Field
        if i.has_key('F'):
            for j in i['F']:
                if j.has_key('FId'):
                    data.AddTwo(id,j['FId'])
                    
        # add Journal
        if i.has_key('J') and i['J'].has_key('JId'):
            data.AddTwo(id, i['J']['JId'])
        # add conference
        if i.has_key('C') and i['C'].has_key('CId'):
            data.AddTwo(id,i['C']['CId'])


# request
# 0 ~~ Id = ? 
# 1 ~~ AuId = ?
# 2 ~~ RId = ?

def GetData(id, cls, ofs = 0):
    url = prefix
    if cls==0:
        url += 'Id=%d'%id
        url += suffix %ofs
    elif cls==1:
        url += 'Composite(AA.AuId=%d)'%id
        url += suffix % ofs
    else:
        url += 'RId=%d'%id
        url += onlyId %ofs
    #url += suffix % ofs
    res = requests.get(url)
    d = json.loads(res.text)
    if len(d['entities'])==10000:
        print 'error!!'
    # 这个地方可能不合适
    AddEdge(d['entities'])
    
    return d['entities']
    
def IsId(id, d):
    if len(d)>0 and d[0]['Id']==id and d[0].has_key('AA'):
        return True
    return False
   
def AddId2Id(a, b, da, db):
    #da = GetData(a, 0)
    for i in da:
        if i.has_key('RId'):
            if not USE_MULTI_THREAD:
                # get one by one
                for j in i['RId']:
                    GetData(j,0)
            else:
                #use multi-thread
                thrd = []
                for j in i['RId']:
                    thrd.append(MultiGet(j,0))
                for j in thrd:
                    j.start()
                for j in thrd:
                    j.join()
    
    for i in db:
        if i.has_key('CC'):
            thrd = []
            cc = i['CC']
            ofs = 0
            while ofs<cc:
                thrd.append(MultiGet(b,2,ofs))
                ofs += 10000
            for j in thrd:
                j.start()
            for j in thrd:
                j.join()
    #db = GetData(b, 2)
    
def AddId2AuId(a, b, da, db):
    #da = GetData(a, 0)
    for i in da:
        if i.has_key('RId'):
            if not USE_MULTI_THREAD:
                # get one by one
                for j in i['RId']:
                    GetData(j,0)
            else:
                # use multi-thread
                thrd = []
                for j in i['RId']:
                    thrd.append(MultiGet(j,0))
                for j in thrd:
                    j.start()
                for j in thrd:
                    j.join()
    #db = GetData(b, 1)

def AddAuId2Id(a, b, da, db):
    #GetData(a, 1)
    for i in db:
        if i.has_key('CC'):
            thrd = []
            cc = i['CC']
            ofs = 0
            while ofs<cc:
                thrd.append(MultiGet(b,2,ofs))
                ofs += 10000
            #print len(thrd)
            for j in thrd:
                j.start()
            for j in thrd:
                j.join()
    #GetData(b, 2)

def AddAuId2AuId(a, b, da, db):
    #GetData(a, 1)
    #GetData(b, 1)
    return

def CalcAllPath(a, b):
    st = time.time()
    data.init()
    thrd = []
    thrd.append(MultiGet(a,0))
    thrd.append(MultiGet(a,1))
    thrd.append(MultiGet(b,0))
    thrd.append(MultiGet(b,1))
    for i in thrd:
        i.start()
    for i in thrd:
        i.join()
    IsIda = IsId(a, thrd[0].d)
    IsIdb = IsId(b, thrd[2].d)
    print a,IsIda
    print b,IsIdb
    ed = time.time()
    print 'identify: ',ed-st
    st = time.time()
    if IsIda and IsIdb:
        AddId2Id(a, b, thrd[0].d,thrd[2].d)
    elif IsIda and not IsIdb:
        AddId2AuId(a, b, thrd[0].d,thrd[3].d)
    elif not IsIda and IsIdb:
        AddAuId2Id(a,b, thrd[1].d,thrd[2].d)
    else:
        AddAuId2AuId(a, b, thrd[1].d,thrd[3].d)
    ed = time.time()
    print 'http request & add edge: ',ed-st
    st = time.time()
    data.FindPath(a, b)
    ed = time.time()
    print 'find path: ',ed-st
    print 'total path: ',len(data.allpath)
    return json.dumps(data.allpath)
