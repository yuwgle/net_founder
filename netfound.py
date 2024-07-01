import requests
import socket
import paramiko
import pythonping
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import ConnectTimeout,ConnectionError


import asyncio
import re

PREFIX = "10.10.20."
RANGE=[1,20]

SSH_USERNAME="ubuntu"
SSH_PASSWORD=" "


def https_request_pattern(ip, port, protocol : str, pattern : str) -> str:
    if pattern in PATTERN_CACHE:
        pt = PATTERN_CACHE.get(pattern)
    else:
        pt = re.compile(pattern, flags=re.IGNORECASE)
        PATTERN_CACHE[pattern] = pt
    try:
        resp = requests.get(f"{protocol}://{ip}:{port}", timeout=3, verify=False)
        if resp.status_code == 200:
            text = resp.text
            matches = pt.findall(text)
            matches = [x.replace("&nbsp;", " ") for x in matches]
            return " ".join(matches)
    except Exception as e:
        # print(f"[ERROR]ssh:{ip}, error: {e}")
        pass
    return ""

def http_open_browser(ip, port, protocol, value):
    if value:
        import webbrowser
        webbrowser.open(f"{protocol}://{ip}:{port}", new=1)
    return None

def ssh_request_cmd(ip, port, protocol : str, cmd : str) -> str:
    with paramiko.SSHClient() as client:
        try:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, port, username=SSH_USERNAME, password=SSH_PASSWORD, timeout=3)
            cin, cout, cerr = client.exec_command(cmd)
            # print(f"ssh:{ip}, hostname:", str(cout.read()))
            return str(cout.read())
        except paramiko.ssh_exception.AuthenticationException:
            # print(f"[ERROR]ssh:{ip}, auth error")
            return "auth error"
        except Exception as e:
            # print(f"[ERROR]ssh:{ip}, error: {e}")
            return "error"

def test_port_open(ip, port : int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.1)
        result = sock.connect_ex((ip, port))
        return (result == 0)

def ping_info(ip, port, protocol, value="") -> str:
    return f"{pythonping.ping(ip, timeout=3, count=1).rtt_avg_ms}ms"

class PortTester:
    name:str
    port:int
    protocol:str
    test_func:Callable[[str, int], bool]
    info_func:Callable[[str, int, str], str]
    operate_func: Callable[[str, int, str, str], str]

    def __init__(self, name:str, port:int, protocol:str, 
                 test_func:Callable[[str, int], bool]=None, 
                 info_func:Callable[[str, int, str], str]=None,
                 operate_func: Callable[[str, int, str, str], str]=None):
        self.name = name
        self.port = port
        self.protocol = protocol
        self.test_func = test_port_open if test_func is None else test_func
        self.info_func = info_func
        self.operate_func = operate_func
        pass

PORT_TESTS = [
    PortTester("PING", -1, "icmp", test_func=lambda x, y: pythonping.ping(x, timeout=3, count=1).success(), info_func = ping_info, operate_func=ping_info),
    PortTester("HTTP", 80, "http", info_func = lambda x, y, z: https_request_pattern(x, y, z, "<title>(.*)</title>"), operate_func=http_open_browser),
    PortTester("HTTPS", 443, "https", info_func = lambda x, y, z: https_request_pattern(x, y, z, "<title>(.*)</title>"), operate_func=http_open_browser),
    PortTester("SSH", 22, "ssh", info_func = lambda x, y, z: ssh_request_cmd(x, y, z, "hostname")),
]
PATTERN_CACHE = {}

def add_port_tester(pt:PortTester):
    PORT_TESTS.append(pt)

def testip(ip:str, data_func:Callable[[str, str, int, str, Any], None]) -> str:
    # print(ip, " - start")
    protostr = None
    try:
        for idx, pts in enumerate(PORT_TESTS):
            is_open = pts.test_func(ip, pts.port)
            if idx == 0 and not is_open:
                break
            info_data = None
            protostr = pts.protocol
            if pts.info_func:
                info_data = pts.info_func(ip, pts.port, protostr)

            if is_open:
                data_func(pts.name, ip, pts.port, pts.name, info_data)

    except ConnectTimeout as e:
        print(ip, ":", protostr, " time out", e)
        pass
    except ConnectionError as e:
        print(ip, ":", protostr, " error:", e)
        pass
    except Exception as e:
        print(ip, ":", protostr if protostr is not None else "icmp", " error:", e)
        pass

def print_data_func(name, ip, port, protostr, infodata):
    tab = "" if protostr == "icmp" else "\t"
    print(f"{tab}{ip}:{port}: {protostr} ->  {infodata}")

async def main():
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(4)
    tasks = [loop.run_in_executor(executor, testip, f"{PREFIX}{i}", print_data_func) for i in range(RANGE[0], RANGE[1])]
    await asyncio.wait(tasks)

if __name__ == "__main__":
    asyncio.run(main())