#!/usr/bin/python3

import asterisk.manager
import sys, time, pprint

host = "127.0.0.1"
user = "admin"
password = "teletics"

target = ""
conferenceid = ""
done = False
channels = []
channel = ""

def handle_shutdown(event, manager):
    manager.close()

def handle_event(event, manager):
    global channels, channel
    global done
    global target
    global conferenceid

    if (event.name == "CoreShowChannel"):
        log("Got Channel")
        if (event.headers['CallerIDNum'] == target) or (event.headers['ConnectedLineNum'] == target):
            log("Channel is a match")
            channels.append(event.headers['Channel'])
        else:
            log(pprint.pformat(event.headers))

    elif (event.name == "CoreShowChannelsComplete"):
        log("Got Channel List Complete with " + str(len(channels)) + " channels")
        if (len(channels) > 0):

            msg = {'Action': 'Redirect',
                   'ActionID': 'None',
                   'Channel': channels[0],
                   'Context': 'pots',
                   'Exten': '*95' + conferenceid,
                   'Priority': 1
                   }
            if (len(channels) > 1):

                msg.update({'ExtraChannel': channels[1],
                            'ExtraExten': '*95' + conferenceid,
                            'ExtraContext': 'pots',
                            'ExtraPriority': 1})

            log("Sending redirect request")
            response = manager.send_action(msg)
            if (response.get_header("Response") != "Success"):
                log(pprint.pformat(response.headers))

            response = manager.send_action({'Action': 'Redirect',
                                            'ActionID': 'None',
                                            'Channel': channel,
                                            'Context': 'pots',
                                            'Exten': '*95'+conferenceid,
                                            'Priority': 1})

        done=True

    else:
        log("Got unknown event " + str(event.name))

            
def main():
    global conferenceid, target, channel
    
    if (len(sys.argv) != 4):
        log("Wrong number of arguments  (confereceid, target, channel)")
        exit(0)
    
    conferenceid = sys.argv[1]
    target = sys.argv[2]
    channel = sys.argv[3]

    manager = asterisk.manager.Manager()
    try:
        # connect to the manager
        try:
            manager.connect(host)
            manager.login(user, password)

            # register some callbacks
            manager.register_event('Shutdown', handle_shutdown) # shutdown
            manager.register_event('*', handle_event)           # catch all

        
            response = manager.send_action({"Action": "CoreShowChannels",
                                            "ActionID": "None"})
        

            if (response.get_header("Response") == "Success"):
                while not done:
                    time.sleep(1)
        
            exit(0)
        
        except asterisk.manager.ManagerSocketException as e:
            #print "Error connecting to the manager: %s" % e.strerror
            sys.exit(1)
        except asterisk.manager.ManagerAuthException as e:
            #print "Error logging in to the manager: %s" % e.strerror
            sys.exit(1)
        except asterisk.manager.ManagerException as e:
            #print "Error: %s" % e.strerror
            sys.exit(1)
    finally:
        # remember to clean up
        manager.close()


def log(string):

    f = open("/tmp/barge.log","a")
    print(string)
    f.write(string + "\n")
    f.close()

    

main()


