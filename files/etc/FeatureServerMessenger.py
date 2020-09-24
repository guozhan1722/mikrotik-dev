# Version 0.0.2.00
# 0.0.1.1  -  Added FServer.
# 0.0.1.2  -  Fixed a bug that caused a crash if Harness did not respond properly
# - Small fix, fserver format needed semicolon
# 0.0.1.3  -  Another change to make error handling more robust so the script doesn't crash when communication with harness goes wrong.
# 0.0.1.4  -  Sorted out firmware updates through Harness.
# 0.0.1.5  -  Some corrections to getting version data from the Feature Server and Radio
# 0.0.1.6  -  Re-added config updates through Harness.
# 0.0.1.7  -  ATA config updates
# 0.0.1.8  -  ATA firmware updates added
# 0.0.1.8s -  SSH skips host checking for our use case.
# 0.0.1.9  -  HTTPS modifications
# 0.0.1.10 -  Allow commandline parameters to dictate whether HTTP or HTTPS.
# 0.0.1.11 -  Small fix for config flashing to use popen instead.
# 0.0.1.12 -  Remote reboot functionality starting point
# 0.0.1.13 -  Remote reboot fix
# 0.0.1.14 -  Change to the ATA password in HT502 file
# 0.0.2.00  -  Large refactor to accomodate the following
#               - Password changes for ATA and Radio 
#               - A more OOP approach to keep track of data for faster reporting
#               - "Weaving" version information checks

# Python libraries
import sys
import time
import subprocess
import http.client
import urllib.parse
import datetime

# Self defined classes
import Network
from Logger import Log
from HT502 import TelnetATA
from RB411 import RadioSSH

# Logging
communicationLog = Log("/root/MessengerLog")
errorLog = Log("/root/ErrorLog")

# Globals
MAC_ADDRESS = ""
CLOUD_SERVER_DOMAIN = "harness.teletics.com" # "10.0.0.222:3305" # "dev.teletics.com"
URL_PREFIX = "https://"
HTTPS = True

radios = {}
tels = {}
versionQueue = []

# Communication with Webserver
def PerformTransaction(actionDict, data):
    try:
        actionDict['mac'] = MAC_ADDRESS
        actionDict['data'] = data
        params = urllib.parse.urlencode(actionDict)
        # Send data to CloudServer, accept string back. "NextAction_NextTransactionDelay"
        # NextTransactionDelay should be in seconds.

        communicationLog.write("SENDING " + params)

        # send data to Harness
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        conn = None
        if HTTPS:
            conn = http.client.HTTPSConnection(CLOUD_SERVER_DOMAIN)
        else:
            conn = http.client.HTTPConnection(CLOUD_SERVER_DOMAIN)

        conn.request("POST", "/Responder", params, headers)
        response = conn.getresponse()

        # deal with the response.
        result = urllib.parse.unquote(response.read().decode())
        communicationLog.write("RECEIVED " + result)

        return response.status, response.reason, result

    except Exception as e:
        errorLog.write("Error in PerformTransaction")
        errorLog.write(e)
        return "Exception", e, "" # status, reason, result

def ParseCSResponse(dump):
    try:
        dict = {}

        parameterList = dump.split(",")
        for parameter in parameterList:
            if parameter:
                parameter = parameter.split("=")
                dict[parameter[0]] = parameter[1]

        return dict

    except Exception as e:
        dict = {'type': 'page', 'action': 'error', 'wait': 0, 'data': 'Error parsing what was received from Harness.'}
        errorLog.write("Error in ParseCSResponse")
        errorLog.write(e)
        return dict

# Data Gathering
def GetPingData():
    results = ""

    resultTel = Network.PingRange('169.254.1.')
    resultRadio = Network.PingRange('169.254.2.')

    # For every IP in the range we pinged
    for i in range(11, 31):
        # Separate the stations by comma
        if i > 11:
            results += ","

        addressRad = "169.254.2.{}".format(i)
        addressTel = "169.254.1.{}".format(i)

        results += str(i)

        # If ping succeeded, append 1. Otherwise 0.
        if (addressRad in resultRadio):
            results += "$1"
        else:
            results += "$0"

        if (addressTel in resultTel):
            results += ";1"
        else:
            results += ";0"

    return results

def GetFSVersion():
    dump = RunLocalDump('cat /proc/cpuinfo')
    cpuname = ParseColonSeparatedByName(dump, 'model name')
    ker = RunLocalDump('cat /proc/version').split(' ')[2]

    dump = RunLocalDump('cat /proc/meminfo')
    tmem = ParseColonSeparatedByName(dump, 'MemTotal').strip().split(' ')[0]
    fmem = ParseColonSeparatedByName(dump, 'MemFree').strip().split(' ')[0]

    dump = RunLocalDump('cat /etc/banner')
    tver = ParseColonSeparatedByName(dump, 'TVER').strip()
    tcfg = ParseColonSeparatedByName(dump, 'TCFG').strip()
    pver = ParseColonSeparatedByName(dump, 'PVER').strip()
    pcfg = ParseColonSeparatedByName(dump, 'PCFG').strip()
    aver = ParseColonSeparatedByName(dump, 'AVER').strip()
    acfg = ParseColonSeparatedByName(dump, 'ACFG').strip()

    data = ("200$%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (MAC_ADDRESS.strip(), cpuname, ker, tmem, fmem, tver, tcfg, pver, pcfg, aver, acfg))

    return data

def GetTelVersion():
    data = ""
    first = True
    results = Network.PingRange('169.254.1.')

    for address in results:
        if not first:
            data += ","
        first = False

        if address not in tels.keys():
            tels[address] = TelnetATA(address)

        data += tels[address].GetVersion()

    return data

def GetRadioVersion():
    data = ""
    first = True
    results = Network.PingRange('169.254.2.')

    for address in results:
        if not first:
            data += ","
        first = False

        if address not in radios.keys():
            radios[address] = RadioSSH(address)

        data += radios[address].GetVersion()

    return data

def GetVersionData():
    return GetFSVersion() + ";" + GetTelVersion() + ";" + GetRadioVersion()

def GetSignalData():
    data = ""
    first = True
    results = Network.PingRange('169.254.2.')

    for address in results:
        if not first:
            data += ","
        first = False

        if address not in radios.keys():
            radios[address] = RadioSSH(address)

        data += radios[address].GetSignal()

    return data

def GetChannelsData():
    data = ""
    first = True
    results = Network.PingRange('169.254.2.')

    for address in results:
        if not first:
            data += ","
        first = False

        if address not in radios.keys():
            radios[address] = RadioSSH(address)

        data += radios[address].GetChannel()

    return data

def GetFServerData():
    data = "200$"

    logC = RunLocalPipeDump("logread | grep -ic ^").strip()

    unreachable = RunLocalPipeDump("logread | grep -ni unreachable | tail -20").strip().split("\n")
    unreachableC = RunLocalPipeDump("logread | grep -ci unreachable").strip()

    segfault = RunLocalPipeDump("logread | grep -ni segfault | tail -20").strip().split("\n")
    segfaultC = RunLocalPipeDump("logread | grep -ci segfault").strip()

    correction = RunLocalPipeDump("logread | grep -ni correction | tail -20").strip().split("\n")
    correctionC = RunLocalPipeDump("logread | grep -ci correction").strip()

    fortyThousand = RunLocalPipeDump("logread | grep -ni 40000 | tail -20").strip().split("\n")
    fortyThousandC = RunLocalPipeDump("logread | grep -ci 40000").strip()

    lagged = RunLocalPipeDump("logread | grep -ni lagged | tail -20").strip().split("\n")
    laggedC = RunLocalPipeDump("logread | grep -ci lagged").strip()

    data += logC + ";"
    data += unreachableC + "|" + ",".join(unreachable) + ";"
    data += segfaultC + "|" + ",".join(segfault) + ";"
    data += correctionC + "|" + ",".join(correction) + ";"
    data += fortyThousandC + "|" + ",".join(fortyThousand) + ";"
    data += laggedC + "|" + ",".join(lagged)

    return data

def GetTXFailedData():
    data = ""
    first = True
    results = Network.PingRange('169.254.2.')

    for address in results:
        if not first:
            data += ","
        first = False

        if address not in radios.keys():
            radios[address] = RadioSSH(address)

        data += radios[address].GetTXFailed()

    return data

def GetHookData():
    data = ""
    first = True
    results = Network.PingRange('169.254.1.')

    for address in results:
        if not first:
            data += ","
        first = False

        if address not in tels.keys():
            tels[address] = TelnetATA(address)

        data += tels[address].GetHook()

    return data

# Parsing Utilities
def ParseColonSeparatedByName(dump, query):
    dump = dump.split("\n")

    for line in dump:
        line = line.strip()
        if query in line:
            return line.split(":")[1].strip()

# Feature Server Command Line

def RunLocalDump(cmd):
    proc = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    time.sleep(1)

    return out.decode()

def RunLocalPipeDump(cmd):
    commands = cmd.split(' | ')

    proc = subprocess.Popen(commands[0].split(' '), stdin = None, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    prev = proc

    for command in commands[1:]:
        p = subprocess.Popen(command.split(' '), stdin = prev.stdout, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        prev = p

    out, err = prev.communicate()
    prev.wait()

    return out.decode()

# NOTE: Wayne once mentioned that perhaps we should be looking for the eth3 mac address rather than eth0 as that will
#   be the mac that appears on the router that assigns an IP. This is easy to change but will have various effects
#   we'll need to change all of the registered macs in the settings for one, and the other thing is that if there are
#   any single port feature servers somehow using Harness, they will not have an eth3.
def GetMacAddress():
    dump = RunLocalDump("ifconfig")

    for line in dump.split("\n"):
        if "eth0" in line:
            return line.split(" HWaddr ")[1]

def DownloadFSFirmware(directory):
    proc = None

    try:
        proc = subprocess.Popen(['wget', URL_PREFIX + CLOUD_SERVER_DOMAIN + '/' + directory.replace("%2f", "/") + '/' + 'fs-fwr.bin', '-P', '/tmp/'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()

        return True

    except Exception as e:
        return False

def FlashFSFirmware():
    proc = None

    try:
        # we're not quite sure why writing output to a file makes things work, but for now we'll go with it?

        proc = subprocess.call('sysupgrade /tmp/fs-fwr.bin >> /root/upgradelog', shell=True)
        time.sleep(1)

        return True # Not sure that it'll get here, since it should theoretically reboot.

    except Exception as e:
        return False

def DownloadFSConfig(directory):
    proc = None

    try:
        #print ('Path: ' + CLOUD_SERVER_DOMAIN + '/' + directory.replace("%2f", "/") + '/' + 'fs-cfg.tar.gz')

        proc = subprocess.Popen(['wget', URL_PREFIX + CLOUD_SERVER_DOMAIN + '/' + directory.replace("%2f", "/") + '/' + 'fs-cfg.tar.gz', '-P', '/tmp/'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()

        return True

    except Exception as e:
        return False

def FlashFSConfig():
    proc = None

    try:
        #proc = subprocess.call("tar xzf /tmp/fs-cfg.tar.gz -C /etc/", shell=True)
        proc = subprocess.Popen(['tar', 'xzf', '/tmp/fs-cfg.tar.gz', '-C', '/etc/'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        time.sleep(1)

        proc = subprocess.call("reboot", shell=True)
        time.sleep(1)

        return True # Not sure that it'll get here, since it should reboot.

    except Exception as e:
        return False

def FindATAWithMac(mac):
    list = Network.PingRange('169.254.1.')

    for ip in list:
        if address not in tels.keys():
            tels[address] = TelnetATA(address)

        if (mac == tels[address].GetMacAddress().replace(':', '')):
            return ip

def FlashATAFirmware(directory):
    reason = ''

    try:
        directory = directory.replace('%2f', '/')
        url = CLOUD_SERVER_DOMAIN + '/' + directory
        address = FindATAWithMac(directory.split('/')[2])
        result, reason = Network.PingIP(address)

        if (result):
            if address not in tels.keys():
                tels[address] = TelnetATA(address)

            tels[address].UpdateFirmware(url)
            tels[address].Reboot()

            return True, reason

    except Exception as e:
        reason = e

    return False, reason

def FlashATAConfig(directory):
    reason = ''

    try:
        directory = directory.replace('%2f', '/')
        url = CLOUD_SERVER_DOMAIN + '/' + directory
        address = FindATAWithMac(directory.split('/')[2])
        result, reason = Network.PingIP(address)

        if (result):
            if address not in tels.keys():
                tels[address] = TelnetATA(address)

            tels[address].UpdateConfig(url)
            tels[address].Reboot()

            return True, reason

    except Exception as e:
        reason = e
    return False, reason

def RebootDevice(board, num, timeout):
    address = "169.254." + board + "." + num

    tries = 0

    while (not Network.PingIP(address) and tries < int(timeout)):
        tries = tries + 1
        time.sleep(1)

    if (tries < int(timeout)):
        if (board == '5'):
            proc = subprocess.call("reboot", shell = True)
        elif (board == '1'):
            if address not in tels.keys():
                tels[address] = TelnetATA(address)
            tels[address].Reboot()
        elif (board == '2'):
            if address not in radios.keys():
                radios[address] = RadioSSH(address)
            radios[address].Reboot()

        time.sleep(10)

        # wait a timeout again after the reboot and check if it comes back up.
        tries = 0
        while (not Network.PingIP(address) and tries < int(timeout)):
            tries = tries + 1
            time.sleep(1)

        return True, num + "$" +  board + "|rebooted"

    return False, num + "$" +  board + "|timeout"

def ProcessQueue():
    global versionQueue

    if not versionQueue:
        versionQueue = Network.PingRange('169.254.1.') + Network.PingRange('169.254.2.')
        
    address = versionQueue.pop()
    
    if address in tels.keys():
        tels[address].PollVersion()
    elif address in radios.keys():
        radios[address].PollVersion()
    else:
        if ('.1.' in address):
            tels[address] = TelnetATA(address)
        else:
            radios[address] = RadioSSH(address)

if __name__ == "__main__":
    MAC_ADDRESS = GetMacAddress()
    actionDict = {'mac': MAC_ADDRESS, 'type': 'cmd', 'action': 'beat'}
    data = "200$5|rebooted"

    result, reason = Network.PingIP('8.8.8.8')

    # Check parameters to decide if using HTTPS or not.
    if (len(sys.argv) == 3):
        CLOUD_SERVER_DOMAIN = sys.argv[1]
        if (sys.argv[2].lower() in 'true'):
            HTTPS = True
            URL_PREFIX = "https://"
        else:
            HTTPS = False
            URL_PREFIX = "http://"

    # Assuming successful ping out to network, start the main loop.
    if (result):
        while True:
            try:
                ProcessQueue()
                status, reason, result = PerformTransaction(actionDict, data)

                if (status == "Exception"):
                    actionDict['type'] = 'page'
                    actionDict['action'] = 'error'
                    actionDict['wait'] = 0
                    data = "An error occurred while attempting communication with Harness. Exception: " + reason.__class__

                else:
                    actionDict = ParseCSResponse(result)

                # Console/ log diagnostic output and wait.
                if (int(actionDict['wait']) > 0):
                    time.sleep(int(actionDict['wait']) + 1)

                # Depending on what command is, run appropriate Get command.
                if actionDict['type'] == 'page':
                    if actionDict['action'] == "ping":
                        data = GetPingData()
                    elif actionDict['action'] == "version":
                        data = GetVersionData()
                    elif actionDict['action'] == "signal":
                        data = GetSignalData()
                    elif actionDict['action'] == "channel":
                        data = GetChannelsData()
                    elif actionDict['action'] == "fserver":
                        data = GetFServerData()
                    elif actionDict['action'] == "txfailed":
                        data = GetTXFailedData()
                    elif actionDict['action'] == "hook":
                        data = GetHookData()
                    elif actionDict['action'] == "done":
                        actionDict['type'] = 'cmd'
                        actionDict['action'] = 'beat'
                        data = "none"
                    elif actionDict['action'] == 'error':
                        errorLog.write("Received 'error' as action.")
                    else:
                        errorLog.write("Received " + actionDict['action'] + " as action. This is an unexpected value.")
                        data = "REQ page: " + actionDict['action']
                        actionDict['action'] = 'error'

                elif actionDict['type'] == 'update':
                    if 'fs' in actionDict['action']:
                        if 'fwr' in actionDict['action']:
                            DownloadFSFirmware(actionDict['action'])
                            FlashFSFirmware()
                        if 'cfg' in actionDict['action']:
                            DownloadFSConfig(actionDict['action'])
                            FlashFSConfig()

                    if 'tel' in actionDict['action']:
                        if 'fwr' in actionDict['action']:
                            result, reason = FlashATAFirmware(actionDict['action'])
                            if (result):
                                data = "success"
                            else:
                                data = reason
                        if 'cfg' in actionDict['action']:
                            result, reason = FlashATAConfig(actionDict['action'])
                            if (result):
                                data = "success"
                            else:
                                data = reason

                elif actionDict['type'] == 'cmd':
                    if actionDict['action'] == 'beat':
                        data = "none"
                    elif actionDict['action'] == 'reboot':
                        num = actionDict['data'].split('$')[0]
                        board = actionDict['data'].split('$')[1].split('|')[0]
                        timeout = actionDict['data'].split('$')[1].split('|')[1]
                        result, data = RebootDevice(board, num, timeout)

            except Exception as E:
                # Log some information.
                errorLog.write("Hit the catch all exception!")

                data = "hit the catch all exception"
                actionDict['type'] = 'page'
                actionDict['action'] = 'error'
                actionDict['wait'] = 0
                time.sleep(5)
    else:
        print (reason)