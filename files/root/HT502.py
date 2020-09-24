import telnetlib
import time

class telnet:

    def __init__(self, address):
        self.session = None
        self.Connect(address)

    def Connect(self, address):
        if (self.session is None):
            self.session = telnetlib.Telnet(address)
            self.ReadUntil('Password:')
            self.Write('t3l3t158')
            self.ReadUntil('>')
            self.address = address
        elif (self.address != address):
            self.Disconnect()
            return self.Connect(address)

    def Disconnect(self):
        self.Write('exit')
        self.ReadAll()
        self.session = None

    def Reboot(self):
        if (self.session is None):
            self.Connect(self.address)
        self.Write('reboot')
        time.sleep(5)
        self.session = None

    def Write(self, cmd):
        if (self.session is None):
            self.Connect(self.address)
        self.session.write((cmd + '\n').encode())

    def ReadUntil(self, prompt):
        if (self.session is None):
            self.Connect(self.address)
        return self.session.read_until(prompt.encode()).decode()

    def ReadAll(self):
        if (self.session is None):
            self.Connect(self.address)
        return self.session.read_all().decode()

    def GetPValue(self, val):
        if (self.session is None):
            self.Connect(self.address)

        self.Write('config')
        self.Write('get ' + val)
        self.Write('exit')
        self.Write('exit')

        dump = self.ReadAll()

        self.session = None

        for line in dump.split('\n'):
            if (val + ' =') in line:
                return line.split(' = ')[1].strip()

    def SetPValue(self, pval, val):
        if (self.session is None):
            self.Connect(self.address)

        self.Write('config')
        self.Write('set ' + pval + ' ' + val)
        self.Write('exit')

    def CommitConfig(self):
        self.Write('config')
        self.Write('commit')
        self.Write('exit')

    def GetStatus(self):
        self.Write('status')
        self.Write('exit')

        ret = self.ReadAll()
        self.session = None
        return ret

    def GetMacAddress(self):
        dump = self.GetStatus()
        for line in dump.split('\n'):
            if ("MAC Address" in line):
                return line.split(" ")[2].strip()

    def GetMFG(self):
        return self.GetPValue('82')
        
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

    def SetFirmwareCheck(self, val):
        # 0 - always check, 2 - always skip
        if (val):
            self.SetPValue('238', '0')
        else:
            self.SetPValue('238', '2')

    def SetDefaultRouter(self, ip):
        ip = ip.split('.')
        self.SetPValue('17', ip[0])
        self.SetPValue('18', ip[1])
        self.SetPValue('19', ip[2])
        self.SetPValue('20', ip[3])

    def SetDNS1(self, ip):
        ip = ip.split('.')
        self.SetPValue('21', ip[0])
        self.SetPValue('22', ip[1])
        self.SetPValue('23', ip[2])
        self.SetPValue('24', ip[3])

    def SetDNS2(self, ip):
        ip = ip.split('.')
        self.SetPValue('25', ip[0])
        self.SetPValue('26', ip[1])
        self.SetPValue('27', ip[2])
        self.SetPValue('28', ip[3])

    def UpdateConfig(self, url):
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

