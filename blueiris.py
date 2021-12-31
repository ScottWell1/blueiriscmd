#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Original concept by: Magnus Appelquist 2014-06-02
# Forked 2021-12-30 Scott W
# - Update for python3
# - add camera enable/disable functions
#

import requests, json, hashlib, sys, argparse

def main():
    parser = argparse.ArgumentParser(description='Blue Iris controller', prog='blueiris')
    parser.add_argument("--host", help="Blue Iris host to connect to ", required=True)
    parser.add_argument('--user', help='User to use when connecting', required=True)
    parser.add_argument('--password', help='Password to use when connecting', required=True)
    parser.add_argument('--debug', action='store_true', help='Print debug messages')
    parser.add_argument('--list-profiles', action='store_true', help='List all available profiles')
    parser.add_argument('--set-profile', action='store', help='Set current profile', metavar='profile-name', default=None)
    parser.add_argument('--set-schedule', action='store', help='Set current schedule', metavar='schedule-name', default=None)
    parser.add_argument('--set-signal', action='store', help='Set current signal', metavar='signal-name', default=None, choices=['red','yellow','green'])
    parser.add_argument('--trigger', action='store', help='Trigger camera', metavar='camera-short-name', default=None)
    parser.add_argument('--ptzbutton', action='store', help='Send PTZ Button Number', metavar='ptz-button-name', default=None)
    parser.add_argument('--ptzcam', action='store', help='Send PTZ Command', metavar='ptz-cam-name', default=None)
    parser.add_argument('--enable', action='store', help='Enable named camera', metavar='camera-short-name', default=None)	
    parser.add_argument('--disable', action='store', help='Disable named camera', metavar='camera-short-name', default=None)

    myargs = parser.parse_args()
	
    bi = BlueIris(myargs.host, myargs.user, myargs.password, myargs.debug)
    print(f"Profile {bi.get_profile()} is active.") 
    print(f"Schedule {bi.get_schedule()}")
    print(f"Signal is {bi.get_signal()}")

    if myargs.list_profiles:
        print("Available profiles are:")
        print(", ".join(bi.profiles_list))

    if myargs.set_profile:
        try:
            profile_id = bi.profiles_list.index(myargs.set_profile)
        except:
            print("Could not find any profile with that name. Use --list-profiles to see available profiles.")
            sys.exit(0)
        #print "Setting active profile to '%s' (id: %d)" % (myargs.set_profile, profile_id)
        print(f"Setting active profile to {myargs.set_profile} (id: {profile_id}")
        bi.cmd("status", {"profile": profile_id})

    if myargs.set_signal:
        signal = bi.get_signal()
        #print "Switching signal %s -> %s" % (signal, myargs.set_signal)
        print(f"Switching signal {signal} -> {myargs.set_signal}")
        bi.set_signal(myargs.set_signal)

    if myargs.set_schedule:
        schedule = bi.get_schedule()
        #print "Switching schedule %s -> %s" % (schedule, myargs.set_schedule)
        print(f"Switching schedule {schedule} -> {myargs.set_schedule}")
        bi.set_schedule(myargs.set_schedule)

    if myargs.trigger:
        #print "Triggering camera '%s'" % myargs.trigger
        print(f"Triggering camera {myargs.trigger}")
        bi.cmd("trigger", {"camera": myargs.trigger})
        
    if myargs.disable:
        print(f'Disabling camera {myargs.disable}')
        bi.cmd("camconfig", {"camera":myargs.disable,"enable":False})
		
    if myargs.enable:
        print(f'Enabling camera {myargs.enable}')
        bi.cmd("camconfig", {"camera":myargs.enable,"enable":True})
		
    if myargs.ptzbutton:
        #0: Pan left
        #1: Pan right
        #2: Tilt up
        #3: Tilt down
        #4: Center or home (if supported by camera)
        #5: Zoom in
        #6: Zoom out
        #8..10: Power mode, 50, 60, or outdoor
        #11..26: Brightness 0-15
        #27..33: Contrast 0-6
        #34..35: IR on, off
        #101..120: Go to preset position 1..20
        if not myargs.ptzcam:
            print("Using --ptzcmdnum requires argument --ptzcam with valid Cam Name..")
            sys.exit(0)
        #print "Sending PTZ Command Button:" + myargs.ptzbutton + " to Cam: " + myargs.ptzcam
        print(f"Sending PTZ Command Button: {myargs.ptzbutton} to Cam: {myargs.ptzcam}")		
        bi.cmd("ptz", {"camera": myargs.ptzcam,"button": int(myargs.ptzbutton),"updown": 0})

    bi.logout()
    sys.exit(0)

class BlueIris:
    session = None
    response = None
    signals = ['red', 'green', 'yellow']

    def __init__(self, host, user, password, debug=False):
        self.host = host
        self.user = user
        self.password = password
        self.debug = debug
        self.url = "http://"+host+"/json"
        r = requests.post(self.url, data=json.dumps({"cmd":"login"}))
        if r.status_code != 200:
            print(r.status_code)
            print(r.text)
            sys.exit(1)

        self.session = r.json()["session"]
        #self.response = hashlib.md5("%s:%s:%s" % (user, self.session, password)).hexdigest()
        self.response = hashlib.md5(str(f"{user}:{self.session}:{password}").encode('utf-8')).hexdigest()
        if self.debug:
            print(f"session: {self.session} response {self.response}")

        r = requests.post(self.url, data=json.dumps({"cmd":"login", "session": self.session, "response": self.response}))
        if r.status_code != 200 or r.json()["result"] != "success":
            print(r.status_code)
            print(r.text)
            sys.exit(1)
        self.system_name = r.json()["data"]["system name"]
        self.profiles_list = r.json()["data"]["profiles"]

        print(f"Connected to {self.system_name}")

    def cmd(self, cmd, params=dict()):
        myargs = {"session": self.session, "cmd": cmd}
        myargs.update(params)

        # print self.url
        # print "Sending Data: "
        # print json.dumps(args)
        r = requests.post(self.url, data=json.dumps(myargs))

        if r.status_code != 200:
            print(r.status_code)
            print(r.text)
            sys.exit(1)
        else:
            pass
            #print "success: " + str(r.status_code)
            #print r.text

        if self.debug:
            print(str(r.json()))

        try:
            return r.json()["data"]
        except:
            return r.json()

    def get_profile(self):
        r = self.cmd("status")
        profile_id = int(r["profile"])
        if profile_id == -1:
            return "Undefined"
        return self.profiles_list[profile_id]

    def get_signal(self):
        r = self.cmd("status")
        signal_id = int(r["signal"])
        return self.signals[signal_id]

    def get_schedule(self):
        r = self.cmd("status")
        schedule = r["schedule"]
        return schedule

    def set_signal(self, signal_name):
        signal_id = self.signals.index(signal_name)
        self.cmd("status", {"signal": signal_id})

    def set_schedule(self, schedule_name):
        self.cmd("status", {"schedule": schedule_name})

    def logout(self):
        self.cmd("logout")

if __name__ == "__main__":
    main()
