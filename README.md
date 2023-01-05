# autounifi
autounifi is an Python Script to automate Access Point Radio Configuration in a Ubiquiti Unifi Controller v7.3.76

You can configure AP radio configurations in seconds every one at the same time.
We only need an Excel file where parameters are especified (for example: Channel, Channel Width, Power Mode, RSSI, MESH, etc.)

The Python Script gets these parameters from the Excel file and through UniFi REST API sends them to UniFi Controller to apply changes.
All parameters in an Acess Point are especified in the json file called parameters.json and it means all these parameters can be modified. The form of send data is in the "payload" variable in autounifi.py file.

Note: When an AP is modified, it restarts itself and keeps offline for a few seconds to apply changes. If the python script send data to an especified AP that already have the same configuration, the AP does not restart itself
