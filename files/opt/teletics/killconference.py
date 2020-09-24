#!/usr/bin/python3

# killconference.py <confbridge id>
#
# Connects to the management socket and kills the conference indicated on the command line
# on the condition that there are no marked users still in the conference.
# 
# This is used in the "hangup" catch in the "pa" macro to make sure the PAs are all
# kicked out of the conference if something goes wrong in setting up the conference (ie. if the 
# user that reqested the conference gets disconnected before entering it)
#

import asterisk.manager
import sys, time

host = "127.0.0.1"
user = "admin"
password = "teletics"

conferenceid = ""
done = False
users = []
markeduser = False
logging = False

def handle_shutdown(event, manager):
    manager.close()

def handle_event(event, manager):
    global markeduser
    global users
    global done
    
    if (event.name == "ConfbridgeList"):
        log("Got event " + str(event.name))
        log("test" + str(event.headers))
        user = {"channel": event.get_header("Channel") }
        users.append(str(event.get_header("Channel")))
        log(str(users))
        if event.get_header("MarkedUser") == "Yes":
            log("Found marked user")
            markeduser = True

    # if the conference we are interested in is ending then we are done        
    elif (event.name == "ConfbridgeEnd"):
        log("Got event " + str(event.name))
        if (event.get_header("Conference") == conferenceid):
            done = True
            
    elif (event.name == "ConfbridgeListComplete"):
        log("Got event " + str(event.name))
        if markeduser == False:
            log("Checking users")
            for user in users:

                log("Kicking user " + user)

                msg = {"Action": "ConfbridgeKick",
                       "Conference": conferenceid,
                       "Channel": user }
               
                resp = manager.send_action(msg)
                log(str(resp))

        # If a marked user was found then we dont want to kick anyone
        else:       
            done=True

    else:
        log("Unknown event " + str(event.name))
            
def main():
    global conferenceid
    
    if (len(sys.argv) != 2):
        log("Wrong number of arguments")
        exit(0)
    
    conferenceid = sys.argv[1]

    manager = asterisk.manager.Manager()
    try:
        # connect to the manager
        try:
            manager.connect(host)
            manager.login(user, password)

            # register some callbacks
            manager.register_event('Shutdown', handle_shutdown) # shutdown
            manager.register_event('*', handle_event)           # catch all

            log("Getting conference list")
            response = manager.send_action({"Action": "ConfbridgeList",
                                            "Conference": conferenceid})
        
            log(response.get_header("Response"))
            if (response.get_header("Response") == "Success"):
                while not done:
                    time.sleep(1)
        
            exit(0)
        
        except asterisk.manager.ManagerSocketException as e:
            log("Error connecting to the manager: %s" % e.strerror)
            sys.exit(1)
        except asterisk.manager.ManagerAuthException as e:
            log("Error logging in to the manager: %s" % e.strerror)
            sys.exit(1)
        except asterisk.manager.ManagerException as e:
            log("Error: %s" % e.strerror)
            sys.exit(1)
    finally:
        # remember to clean up
        log("Closing")
        manager.close()

def log(string):
    global logging

    if logging == True:
        f = open("/tmp/killconference.log","a")
        print(string)
        f.write(string + "\n")
        f.close()

main()
