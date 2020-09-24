#!/usr/bin/python3

import argparse, random, subprocess


def main():
    filename = "/tmp/callfile-" + str(random.randint(10000, 99000)) + ".txt"

    parser = argparse.ArgumentParser(description='Create an outbound call')
    parser.add_argument('--channel', help='Channel to originate from', required=True)
    parser.add_argument('--callerid', help='Caller ID from the source', required=True)

    parser.add_argument('--application', help='Application to connect to')
    parser.add_argument('--data', help='Data for the application')

    parser.add_argument('--context', help='Context for the destination')
    parser.add_argument('--extension', help='Extension within the context')
    parser.add_argument('--priority', help='Priority within the extension')

    args = parser.parse_args()

    log(str(args))

    output = open(filename, 'w')
    output.write("Channel: " + str(args.channel) + "\n")
    output.write("CallerID: " + str(args.callerid) + "\n")

    if (args.application is not None):

        output.write("Application: " + str(args.application) + "\n")
        output.write("Data: " + str(args.data) + "\n")

    else:
        output.write("Context: " + str(args.context) + "\n")
        output.write("Extension: " + str(args.extension) + "\n")
        output.write("Priority: " + str(args.priority) + "\n")


    output.close()
    subprocess.call(["/bin/mv",filename, "/tmp/spool/asterisk/outgoing/"])
#    subprocess.call(["/bin/mv", filename, "/tmp/test.txt"])


def log(string):
    f = open("/tmp/callfile.log","a")
    print(string)
    f.write(string + "\n")
    f.close()

main()
