# coding: utf-8

import socket
import main
import copy

HOST = ''
PORT = 8300

quest = {}
tot = 0
ans = []

# Configure Socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
text_content = '''HTTP/1.0 200 OK
Server: python
Date: Fri, 01 Aug 2014 06:44:11 GMT
Content-Type: application/json

'''

while True:
    s.listen(3)
    conn,addr = s.accept()
    res = conn.recv(1024)
    method = res.split(' ')[0]
    f = open('2.out','w+')
    f.write(res)
    if method == 'GET':
        f.write(res)
        print res.split(' ')[1]
        req = res.split(' ')[1]
        req = req.strip('//?') # id2=3242&id1=12839
        dc = {}
        for i in req.split('&'):
            j = i.split('=')
            dc[j[0].lower()]=long(j[1])
        a=dc['id1']
        b=dc['id2']
        res = main.CalcAllPath(a,b)
        #if quest.has_key((a,b)):
        #    res = ans[quest[(a,b)]]
        #else:
        #    res = main.CalcAllPath(a,b)
        #    quest[(b,a)] = tot
        #    tot += 1
        #    ans.append(copy.deepcopy(res))
        conn.sendall(text_content+res)
    f.close()            
    #f.flush()
    conn.close()
