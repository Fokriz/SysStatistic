import socket
import time
from threading import Thread
from datetime import datetime

menu = """
1 - Available connections
2 - Get information from client
3 - Interrupt one available connection
quit - Quit
"""

sock = socket.socket()
sock.bind(('127.0.0.1', 3938))
sock.listen(5)
connections = dict()
logs = list()

def log(statement, flag=False):
    logs.append(statement)
    if flag:
        print(statement)

class Executor(Thread):
    def printConnections(self):
        for ip in connections:
            print(ip)

    def save(self, filename, data):
        file = open(filename, "w")
        file.write(data)

    def get(self, ip, file_type):
        conn = connections[ip]
        conn.send(bytes("html", 'utf-8'))
        time.sleep(1)
        data = conn.recv(4096).decode('utf-8')
        self.save(filename, data)

    def interruptConnection(self, ip):
        conn = connections[ip]
        conn.send(bytes("break", 'utf-8'))
        conn.close()
        connections.pop(ip)

    def run(self):
        log("Program has started", True)
        log(datetime.now(), True)
        while True:
            try:
                print(menu)
                key = input("Enter a command: ")
                if key == "1":
                    self.printConnections()
                if key == "2":
                    ip_port = input("Enter the IP and port of the connection, separated by a space: ")
                    ip = ip_port.split(" ")[0]
                    port = ip_port.split(" ")[1]
                    file_type = "html"
                    self.get((ip, int(port)), file_type)
                    log("Received data from server.", True)
                    log(datetime.now(), True)
                if key == "3":
                    ip_port = input("Enter the IP and port of the connection, separated by a space: ")
                    ip = ip_port.split(" ")[0]
                    port = ip_port.split(" ")[1]
                    self.interruptConnection((ip, int(port)))
                    log("Connection interrupted: " + str((ip, int(port))), True)
                    log(datetime.now(), True)
                if key == "quit":
                    log("Closing program...", True)
                    log(datetime.now(), True)
                    sock.close()
                    break
            except KeyError:
                print("Wrong IP or port, please try again")
                log("Wrong IP error has occurred!")
                log(datetime.now())
            except Exception:
                log("Unexpected error has occurred!")
                log(datetime.now())

executor = Executor().start()

class Acceptor(Thread):
    def __init__(self):
        self.daemon = True

    while True:
        try:
            conn, addr = sock.accept()
            if conn is not None:
                connections[addr] = conn
                log("\nConnection established: " + str(addr), True)
                log(datetime.now(), True)
            time.sleep(1)
        except Exception:
            log("\nERORR!", True)
            log(datetime.now(), True)

acceptor = Acceptor().start()
