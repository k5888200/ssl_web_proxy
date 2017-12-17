#!/usr/bin/python3

import socket, ssl, threading, re, sys, os, subprocess, copy
from OpenSSL import SSL


bindsocket = socket.socket()
bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # reuse address option
bindsocket.bind(('', 4433))
bindsocket.listen(1024)



def enter_client(client, addr):
    firstData = client.recv(2048).decode()
    if not firstData.startswith("CONNECT"): return
    host, port= re.search("Host: ([\w.-:]*)", firstData).group(1).split(":")
    port = int(port)
    server = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    server.connect((host, port))

    client.send('HTTP/1.1 200 Connection established\r\nConnection: close\r\n\r\n'.encode())
    
    certPath = os.path.join("cert", host+".pem")
    if not os.path.isfile(certPath):
        subprocess.call("cd cert;./_make_site.sh " + host, shell=True)

    client = ssl.wrap_socket(client, certfile=certPath, server_side=True)
    
    buf = client.recv(1024)
    S = copy.deepcopy(buf)
    while len(buf) < 1024:
        buf = client.recv(1024)
        S += buf
    if S: server.send(S)


    buf = server.recv(1024)
    S = copy.deepcopy(buf)
    while len(buf) < 1024:
        buf += server.recv(1024)
        S += buf
    if S: client.send(S)

    server.close()
    client.close()
    






subprocess.call("cd cert;./_clear_site.sh", shell=True)
subprocess.call("cd cert;./_make_root.sh kimtaeyang", shell=True)
subprocess.call("cd cert;./_init_site.sh", shell=True)


threads = []
while True:
    clientSocket, addr = bindsocket.accept()
    t = threading.Thread(target = enter_client, args=(clientSocket,addr))
    t.start()
    threads.append(t)
    continue
    connstream = ssl.wrap_socket(newsocket, server_side=True, certfile="cert/facebook.com.pem", keyfile="cert/facebook.com.pem")
    try:
        deal_with_client(connstream)
    finally:
        connstream.shutdown(socket.SHUT_RDWR)
        connstream.close()
    break

for t in threads: t.join()
