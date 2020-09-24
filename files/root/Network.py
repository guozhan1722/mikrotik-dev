import subprocess
import time

def PingIP(address):
    # For the times when we need to ping a particular address
    proc = None
    try:
        proc = subprocess.Popen(['ping', '-c', '3', address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        time.sleep(1)
        
        for line in out.decode().split('\n'):
            if 'transmitted' in line and not '0 packets received' in line:
                return True, ''
    except Exception as e:
        return False, e
    return False, 'Ping of address ' + address + ' failed.'

def PingRange(baseIP):
    results = []
    proc = None
    try:
        proc = subprocess.Popen(['ash', '/root/PingAll.sh', baseIP], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        time.sleep(1)
        for line in out.decode().split("\n"):
            line = line.strip()
            if (line != ''):
                results.append(line)
    except Exception as e:
        raise e
    return results
