import requests, json, urllib3, pandas

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONSTANTS

gateway = {"ip": "YOUR IP ADDRESS", "port": "8443"}

headers = {"Accept": "application/json", "Content-Type": "application/json"}

credentials = {
    "username": "username",
    "password": "password"
}

# SESION ESTABLISHMENT ON UNIFI
session = requests.Session()

# LOGIN

url_login = "https://{}:{}/api/login".format(gateway["ip"], gateway["port"])
response_login = session.post(url_login, headers=headers, data=json.dumps(credentials), verify=False)

# GET APs' IDENTIFIERS

url_devices = "https://{}:{}/api/s/default/stat/device".format(gateway["ip"], gateway["port"])
response_devices = session.get(url_devices, headers=headers, verify=False)
data_devices = (response_devices.json())['data']

id_devices = {}
for device in data_devices:
    id_devices[device["name"]] = device["_id"]

# EXTRACT PARAMETERS (VALUES) FROM EXCEL

excel = pandas.read_excel('AP Parameters.xlsx', sheet_name='Parameters')
json_parameters = excel.to_json(orient='records')
dict_parameters = json.loads(json_parameters)

# UPDATE OF APs' PARAMETERS

updated_devices = []

for ap in dict_parameters:
  try:
    url_update = "https://{}:{}/api/s/default/rest/device/{}".format(gateway["ip"], gateway["port"], id_devices[ap["NOMBRE"]])

    payload = json.dumps({
      "mesh_sta_vap_enabled": False,
      "radio_table": [
        {
          "name": "wifi0",
          "channel": "{}".format(ap["CH 2.4"]),
          "ht": "{}".format(ap["CH WIDTH 2.4"]),
          "tx_power_mode": "{}".format(ap["TX MODE 2.4"].lower()),
          "min_rssi_enabled": True,
          "min_rssi": ap["RSSI 2.4"]
        },
        {
          "name": "wifi1",
          "channel": "{}".format(ap["CH 5.0"]),
          "ht": "{}".format(ap["CH WIDTH 5.0"]),
          "tx_power_mode": "{}".format(ap["TX MODE 5.0"].lower()),
          "min_rssi_enabled": True,
          "min_rssi": ap["RSSI 5.0"]
        }
      ]
    })

    response = session.put(url_update, headers=headers, data=payload)
    updated_devices.append(id_devices[ap["NOMBRE"]])

    print("* Successful Update: {}".format(ap["NOMBRE"]))

  except:
    print("- Name not found: {}".format(ap["NOMBRE"]))

# RESULTS PRINTED

print("\n\nAPs UPDATED CONFIGURATION \n")

response_devices = session.get(url_devices, headers=headers, verify=False)
data_devices = (response_devices.json())['data']

for device in data_devices:

  if device['_id'] in updated_devices:
    print(f"DEVICE: {device['name']}")

    if device['state'] == 1:
      print('- State:               online')
    else:
      print('- State:               offline')

    print(f"- IP:                  {device['ip']}")
    print(f"- MAC:                 {device['mac']}")
    print(f"- DHCP:                {device['config_network']['type']}")
    print("* 2.4GHz Parameters")
    print(f"  - Channel:           {device['radio_table'][0]['channel']}")
    print(f"  - RSSI:              {device['radio_table'][0]['min_rssi']}dBm")
    print(f"  - Power Transmit:    {device['radio_table'][0]['tx_power_mode']}")
    print("* 5.0GHz Parameters")
    print(f"  - Channel:           {device['radio_table'][1]['channel']}")
    print(f"  - RSSI:              {device['radio_table'][1]['min_rssi']}dBm")
    print(f"  - Power Transmit:    {device['radio_table'][1]['tx_power_mode']}\n")