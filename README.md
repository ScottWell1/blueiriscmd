blueiriscmd
===========

Python cmd tool to communicate with BlueIris Camera surveillance software API.

Blue Iris has a json API that allows reading status, triggering events, changing profiles, enabling/disabling cameras, and so forth. This python tool provides a command line utility to interact with BlueIris using it's json API.

Example to change current profile to "Home":

    blueiris.py --host 192.168.1.100:17001 --user username --password password  --set-profile Home
    Connected to 'My place'
    Profile 'Away' is active
    Setting active profile to 'Home' (id: 2)

This command will trigger event on camera "garage":

    blueiris.py --host 192.168.1.100:17001 --user username --password password --trigger garage
    Connected to 'My place'
    Profile 'Borta' is active
    Triggering camera 'garage'

This command will set a camera's state to "enabled":

    blueiris.py --host 192.168.1.100:17001 --user username --password password --enable garage
    Connected to 'My place'
    Profile 'Borta' is active
    Enabling camera 'garage'

Full API is not yet implemented, but feel free to add what you need.

More information regarding Blue Iris can be found here:
http://blueirissoftware.com/


