import socket
import sys
import time
import psutil
import platform
import os
import pandas as pds

if len(sys.argv) < 2:
    print("Try again using configuration file as a first argument.")
    sys.exit()
filename = str(sys.argv[1])
if not filename.endswith(".ini"):
    print("Use .ini file as a first argument.")
    sys.exit()

def config_parser(file_name):
    try:
        d = dict()
        configuration = open(file_name, "r").readlines()
        for line in configuration:
            key = line.split("=")[0]
            value = line.split("=")[1].replace("\n", "")
            d[key] = value
        return d
    except Exception:
        print("Check configuation file.")
        sys.exit(0)

configuration = config_parser(filename)
ip = configuration.get("address")
port = int(configuration.get("port"))
timeout = int(configuration.get("timeout"))
sock = socket.socket()
sock.connect((ip, port))

def send(filename):
    file = open(filename, "r")
    for line in file.readlines():
        sock.send(bytes(line, 'utf-8'))

def fill():
    f = open("data.txt", "w")
    f.write("Operation System="+platform.system()+"\n")
    f.write("CPU name={}\n".format(platform.processor()))
    f.write("CPU load={}\n".format(psutil.cpu_percent()))
    f.write("CPU cores={}\n".format(psutil.cpu_count()))
    d = dict(psutil.cpu_freq()._asdict())
    f.write("Current CPU frequency={}\n".format(int(d.get('current'))))
    f.write("Minimal CPU frequency={}\n".format(int(d.get('min'))))
    f.write("Maximum CPU frequency={}\n".format(int(d.get('max'))))
    d = dict(psutil.virtual_memory()._asdict())
    f.write("Free memory(MiB)={}\n".format(int(d.get('free')/2**20)))
    f.write("Processes count={}\n".format(len(psutil.pids())))
    f.write("Active user={}\n".format(os.getlogin()))
    path = None
    if platform.system() == 'Windows':
        path = "C:\\"
    elif platform.system() == "Linux":
        path = "/"
    size = int(psutil.disk_usage(path).free)/(2**30)
    f.write("Free space on {}(GiB)={}\n".format(path, size))
    return "data.txt"

def fill_txt():
    fill()
    f = open('data.txt', 'r')
    content = f.readlines()

    template_open = """
    <html>
        <head>
            <meta charset='utf-8'>
            <title>Check os</title>
        </head>
        <body>
    """

    template_close = """
        </body>
    </html>
    """
    out = open('index.html', 'w')
    out.write(template_open)
    d = dict()
    for i in content:
        key = i.split("=")[0]
        value = i.split("=")[1].replace("\n", "")
        d[key] = value
    s = pds.Series(d)
    out.write(s.to_frame('DATA').to_html())
    out.write(template_close)
    return "index.html"

while True:
    data = str(sock.recv(1024), "utf-8")
    if data.startswith("break"):
        break
    if data.startswith("html"):
        send(fill_txt())
    if data.startswith("txt"):
        send(fill())
    if data.startswith("ini"):
        send(filename)
    time.sleep(1)

sock.close()
