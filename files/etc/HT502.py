import telnetlib
import time

class TelnetATA:
    passwords = ["/makes$n#s!nhisLesPaul", "!noutwaltznm~w/me", "teletics"]

    def __init__(self, address):
        self.session = None
        self.address = address
        self.Connect()
        self.PollVersion()
        self.Disconnect()

    def Connect(self):
        if (self.session is None):
            oldPW = False
            connected = False
            
            self.session = telnetlib.Telnet(self.address)
            self.ReadUntil('Password:')
            
            for pw in self.passwords:
                self.Write(pw)
                result = self.ReadUntil('>', 5)
                
                # If it prompts for a password again, the log in failed.
                if "Password:" in result:
                    oldPW = True
                elif ">" in result:
                    connected = True
                    break
            
            if connected and oldPW:
                self.SetPValue('2', self.passwords[0])
                

    def Disconnect(self):
        self.Write('exit')
        self.session = None

    def Reboot(self):
        if (self.session is None):
            self.Connect()
        self.Write('reboot')
        time.sleep(5)
        self.session = None

    def Write(self, cmd):
        if (self.session is None):
            self.Connect()
        self.session.write((cmd + '\n').encode())

    def ReadUntil(self, prompt, timeout = 30):
        if (self.session is None):
            self.Connect()
        return self.session.read_until(prompt.encode(), timeout).decode()

    def GetPValue(self, val):
        if (self.session is None):
            self.Connect()

        self.Write('config')
        self.ReadUntil('>')
        self.Write('get ' + val)
        dump = self.ReadUntil('>')
        self.Write('exit')
        dump = self.ReadUntil('>')

        for line in dump.split('\n'):
            if (val + ' =') in line:
                return line.split(' = ')[1].strip()

    def SetPValue(self, pval, val):
        if (self.session is None):
            self.Connect()

        self.Write('config')
        dump = self.ReadUntil('>')
        self.Write('set ' + pval + ' ' + val)
        dump = self.ReadUntil('>')
        self.Write('exit')
        dump = self.ReadUntil('>')

    def CommitConfig(self):
        if (self.session is None):
            self.Connect()
        self.Write('config')
        dump = self.ReadUntil('>')
        self.Write('commit')
        dump = self.ReadUntil('>')
        self.Write('exit')
        dump = self.ReadUntil('>')

    def GetStatus(self):
        if (self.session is None):
            self.Connect()
        self.Write('status')

        ret = self.ReadUntil('>')
        return ret

    def GetMacAddress(self):
        dump = self.GetStatus()
        for line in dump.split('\n'):
            if ("MAC Address" in line):
                return line.split(" ")[2].strip()

    def GetMFG(self):
        return self.mfg

    def PollVersion(self):
        dump = self.GetStatus()
        self.macAddr = self.ParseStatus(dump, "MAC Address")
        self.model = self.ParseStatus(dump, "Model")
        self.hardwareV = self.ParseStatus(dump, "Hardware").rstrip()
        self.bootV = self.ParseStatus(dump, "Boot").rstrip()
        self.programV = self.ParseStatus(dump, "Program").rstrip()
        self.coreV = self.ParseStatus(dump, "Core").rstrip()
        self.baseV = self.ParseStatus(dump, "Base").rstrip()
        self.mfgV = self.GetPValue('82')
        self.cfgV = "CFG1.0"

    def GetVersion(self):
        ret = ("%s$%s|%s|%s|%s|%s|%s|%s|%s|%s" % (self.address.split('.')[3], self.macAddr, self.model, self.hardwareV, self.programV, self.bootV, self.coreV, self.baseV, self.mfgV, self.cfgV))

        return ret

    def GetHook(self):
        ret = self.address.split(".")[3]

        dump = self.GetStatus()

        port1 = self.ParseDumpByFieldName(dump, "Port 1")[0].split("    ")

        if port1[0].strip() == "On Hook":
            ret += '$1'
        else:
            ret += '$0'
        if port1[1].strip() == "Not Registered":
            ret += '|0'
        else:
            ret += '|1'
        port2 = self.ParseDumpByFieldName(dump, "Port 2")[0].split("    ")
        if port2[0].strip() == "On Hook":
            ret += '|1'
        else:
            ret += '|0'
        if port2[1].strip() == "Not Registered":
            ret += '|0'
        else:
            ret += '|1'

        return ret


    def SetFirmwareCheck(self, bool):
        if (self.session is None):
            self.Connect()
        # 0 - always check, 2 - always skip
        if (bool):
            self.SetPValue('238', '0')
        else:
            self.SetPValue('238', '2')

    def SetDefaultRouter(self, ip):
        if (self.session is None):
            self.Connect()
        ip = ip.split('.')
        self.SetPValue('17', ip[0])
        self.SetPValue('18', ip[1])
        self.SetPValue('19', ip[2])
        self.SetPValue('20', ip[3])

    def SetDNS1(self, ip):
        if (self.session is None):
            self.Connect()
        ip = ip.split('.')
        self.SetPValue('21', ip[0])
        self.SetPValue('22', ip[1])
        self.SetPValue('23', ip[2])
        self.SetPValue('24', ip[3])

    def SetDNS2(self, ip):
        if (self.session is None):
            self.Connect()
        ip = ip.split('.')
        self.SetPValue('25', ip[0])
        self.SetPValue('26', ip[1])
        self.SetPValue('27', ip[2])
        self.SetPValue('28', ip[3])

    def UpdateConfig(self, url):
        if (self.session is None):
            self.Connect()
        # Set Default Router to 169.254.5.200
        self.SetDefaultRouter('169.254.5.200')
        # Set DNS1 to 8.8.8.8
        self.SetDNS1('8.8.8.8')
        # Set DNS2 to 8.8.4.4
        self.SetDNS2('8.8.4.4')
        # Set Config server path to url
        self.SetPValue('237', url)
        # Set always check for new firmware to true
        self.SetFirmwareCheck(True)

        self.CommitConfig()

        time.sleep(5)
        self.Disconnect()

    def UpdateFirmware(self, url):
        if (self.session is None):
            self.Connect()
        # Set Default Router to 169.254.5.200
        self.SetDefaultRouter('169.254.5.200')
        # Set DNS1 to 8.8.8.8
        self.SetDNS1('8.8.8.8')
        # Set DNS2 to 8.8.4.4
        self.SetDNS2('8.8.4.4')
        # Set Config server path to url
        self.SetPValue('192', url)
        # Set always check for new firmware to true
        self.SetFirmwareCheck(True)

        self.CommitConfig()

        time.sleep(5)
        self.Disconnect()

    # Parsing
    def ParseDumpByFieldName(self, dump, query):

        retList = []
        dump = dump.split("\n")
        for line in dump:
            line = line.lstrip()
            if line:
                if query == "Station":
                    lineList = line.split(" ")
                    if lineList[0] == query:
                        retList.append(lineList[1].lstrip())

                else:
                    lineList = line.split(":")
                    if lineList[0] == query:
                        retList.append(line.split(":")[1].lstrip())
        return retList

    def ParseStatus(self, dump, query):
        dump = dump.split('\n')

        for line in dump:
            line = line.strip()
            if query in line:
                if query == 'MAC Address':
                    return line.split(' ')[2].strip()
                elif query == 'Model':
                    return line.split(':')[1].strip().split(" ")[0]
                elif query == 'Hardware':
                    return line.split(' ')[2]
                else:
                    return line.split(' -- ')[1]

if __name__ == '__main__':
    test = TelnetATA("169.254.1.11")
    print(test.GetVersion())
    print(test.GetHook())