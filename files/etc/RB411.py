import sys
import time
import subprocess
import Network

class RadioSSH:

    def __init__(self, address):
        self.session = None
        self.address = address
        self.Execute("echo -e \"/makes$n#s!nhisLesPaul\n/makes$n#s!nhisLesPaul\" | passwd")
        self.PollVersion()

    def Execute(self, cmd):
        proc = subprocess.Popen(['ssh', '-o', 'StrictHostKeyChecking=no', 'root@' + self.address, cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        ret = out.decode()

        return ret

    def Reboot(self):
        self.Execute("reboot")

    def PollVersion(self):
        dump = self.Execute("ifconfig | grep HWaddr | grep adhoc0")
        self.macAddr = dump.split("HWaddr")[1].strip()

        dump = self.Execute("cat /etc/banner")
        for line in dump.split('\n'):
            if 'Teletics OS' in line:
                self.release = line.strip().split(' ')[5]

        self.dmesg = '2013.0.0'

        dump = self.Execute("uci show wireless")
        self.ssid = self.ParseWirelessByFieldName(dump, "ssid")
        self.country = self.ParseWirelessByFieldName(dump, "country")
        self.channel = self.ParseWirelessByFieldName(dump, "channel")
        self.hwmode = self.ParseWirelessByFieldName(dump, "hwmode")
        self.distance = self.ParseWirelessByFieldName(dump, "distance")
        self.txpower = self.ParseWirelessByFieldName(dump, "txpower")
        self.network = self.ParseWirelessByFieldName(dump, "network")
        self.mode = self.ParseWirelessByFieldName(dump, "mode")

        # Default values in case we're on an older version of the radio that doesn't have the required file
        self.rMfgV = "1.0"
        self.rCfgV = "1.0"

        dump = self.Execute("cat /etc/config/version").strip()
        if not "No such file" in dump:
            self.rMfgV, self.rCfgV = dump.split("\n")

    def GetVersion(self):
        ret = ("%s$%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (self.address.split('.')[3], self.macAddr, self.ssid, self.release, self.dmesg, self.country, self.channel, self.hwmode, self.distance, self.txpower, self.network, self.mode, self.rMfgV, self.rCfgV))

        return ret

    def GetSignal(self):
        ret = ""

        dump = self.Execute("iw adhoc0 station dump")

        macList, signalList = self.ParseStationDump(dump)

        signal0 = 0
        dbmMin = 0
        dbmMax = -100
        dbmAvg = 0
        nearMac = "0"

        # Go through each of the found signal values, analyze to find min, max, avg, and the mac with the closest signal source.
        for i in range(0, len(macList)):
            value = signalList[i]
            value = int(value.split(" ")[0])
            if value < dbmMin:
                dbmMin = value
            if value > dbmMax:
                dbmMax = value
                nearMac = macList[i]
            dbmAvg += value

        if len(macList) != 0:
            signal0 = signalList[0].split(" ")[0]
            dbmAvg /= len(macList)

        signal = ""
        noise = ""
        bitRate = ""
        quality = ""

        dump = self.Execute("iwinfo adhoc0 info")

        for line in dump.split("\n"):
            if "Signal:" in line:
                lineSplit = line.strip().split(" ")
                signal = lineSplit[1]
                noise = lineSplit[5]
            if "Bit Rate:" in line:
                bitRate = line.strip().split(" ")[2]
            if "Quality:" in line:
                quality = line.strip().split(" ")[6].split("/")[0]

        ret = ("%s$%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (self.address.split(".")[3], signal0, nearMac, len(signalList), dbmMax, dbmAvg, dbmMin, signal, noise, bitRate, quality))
        return ret

    def GetChannel(self):
        ret = ""

        dump = self.Execute("iwinfo adhoc0 scan")

        cellCtr = 0
        for cell in dump.split("Cell "):
            cellStr = ""
            if cell != "":
                if cellCtr > 0:
                    ret += ","
                cellStr += self.address.split(".")[3] + "$"
                ctr = 0
                for line in cell.split("\n"):
                    line = line.strip()
                    if line != "":
                        if (ctr == 0):
                            cellStr += line.split("-")[0].strip() + "|"
                            cellStr += line.split(" ")[3].strip() + "|"
                        elif (ctr == 1):
                            cellStr += line.split(":")[1].strip()[1:-1] + "|"
                        elif (ctr == 2):
                            cellStr += line.split(":")[2].strip() + "|"
                        elif (ctr == 3):
                            splitLine = line.split(" ")
                            cellStr += splitLine[1] + "|" + splitLine[5] + "|"
                        else:
                            cellStr += line.split(":")[1].strip()
                            if (ctr != 4):
                                cellStr += "|"
                        ctr += 1
                ret += cellStr.replace(",", " ")
                cellCtr += 1
        return ret

    def GetTXFailed(self):
        ret = self.address.split(".")[3] + "$"

        dump = self.Execute("iw adhoc0 station dump")

        count = 0
        firstInSet = True

        # TODO: it's really difficult to trace parsing without being able to look at sample output being parsed.
        # Look to grab some sample output  and document it so it's easier to trace the parse process side by side

        for line in dump.split("\n"):
            line = line.lstrip()
            if line != "":
                if count == 0:
                    if not firstInSet:
                        ret += ";"
                    else:
                        ret += ""
                    ret += line.split(" ")[1] + "|"
                    count = 1
                else:
                    lineList = line.strip().split(":")
                    if lineList[0] == "connected time":
                        count = 0
                        firstInSet = False
                    elif "tx failed" in lineList[0]:
                        ret += lineList[1].lstrip()

        return ret

    # Parsing

    def ParseWirelessByFieldName(self, dump, query):
        dump = dump.split("\n")
        for line in dump:
            line = line.split(".")
            if line and line[-1].split("=")[0] == query:
                return line[-1].split("=")[1].strip()

    # parses "iw adhoc0 station dump", the command returns a list of all signal sources that the station sees
    #   and information about the strength of those signal sources. Sift through the list to form two parallel lists
    #   that correlate the MAC of the source, and the signal strength of that source.
    def ParseStationDump(self, dump):
        macList = []
        signalList = []
        dump = dump.split("\n")
        for line in dump:
            line = line.lstrip()
            if line:
                lineList = line.split(" ")
                if lineList[0] == "Station":
                    macList.append(lineList[1].lstrip())

                lineList = line.split(":")
                if lineList[0] == "signal":
                    signalList.append(line.split(":")[1].lstrip())
        return macList, signalList

if __name__ == '__main__':
    test = RadioSSH("169.254.2.11")
    print (test.GetVersion())
    print (test.GetSignal())
    print (test.GetChannel())
    print (test.GetTXFailed())