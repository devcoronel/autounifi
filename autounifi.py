import requests, json, urllib3, pandas, re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONSTANTS

gateway = {"ip": "X.X.X.X", "port": "8443"}

headers = {"Accept": "application/json", "Content-Type": "application/json"}

credentials = {
    "username": "USERNAME",
    "password": "PASSWORD"
}

excel_name = 'AP Parameters'
sheet_name = 'Parameters'

# SESION ESTABLISHMENT ON UNIFI
session = requests.Session()

# LOGIN

url_login = "https://{}:{}/api/login".format(gateway["ip"], gateway["port"])
response_login = session.post(url_login, headers=headers, data=json.dumps(credentials), verify=False)

# GET APs' IDENTIFIERS AND WIFI NAME

url_devices = "https://{}:{}/api/s/default/stat/device".format(gateway["ip"], gateway["port"])
response_devices = session.get(url_devices, headers=headers, verify=False)
data_devices = (response_devices.json())['data']

id_devices = {}  # APs' IDENTIFIERS NUMBER
wifi_names = {}  # NAME OF WIFI TECHNOLOGY (WIFI0, WIFI1, ETH0, ETH1)
mac_devices = {} # APs' MAC ADDRESS

for device in data_devices:

  id_devices[device["name"]] = device["_id"]
  mac_devices[device["name"]] = device["mac"]

  n_wifi_technologies = len(device['radio_table'])
  
  if n_wifi_technologies != 0:
    names = []
    for i in range(n_wifi_technologies):
      names.append(device['radio_table'][i]['name'])
    wifi_names[device["name"]] = names
  
  else:
    wifi_names[device["name"]] = None

# EXTRACT PARAMETERS (VALUES) FROM EXCEL

excel = pandas.read_excel('{}.xlsx'.format(excel_name), sheet_name='{}'.format(sheet_name))
json_parameters = excel.to_json(orient='records')
dict_parameters = json.loads(json_parameters)

# APs' EXCEL NAMES

ap_excel_names = []
for ap in dict_parameters:
  ap_excel_names.append(ap["NAME"])

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

ap_excel_names.sort(key=natural_keys)

# SELECT APs' TO MODIFY

aps_selected = []

for ap in ap_excel_names:
  if ap_excel_names.index(ap)%4 == 0:
    if len(ap_excel_names) - ap_excel_names.index(ap) < 4:
      if len(ap_excel_names) - ap_excel_names.index(ap) == 3:
        value_col1 = "({}) {}".format(ap_excel_names.index(ap)+1, ap)
        value_col2 = "({}) {}".format(ap_excel_names.index(ap)+2, ap_excel_names[ap_excel_names.index(ap)+1])
        value_col3 = "({}) {}".format(ap_excel_names.index(ap)+3, ap_excel_names[ap_excel_names.index(ap)+2])
        
        print(("{}".format(value_col1)).ljust(35)+("{}".format(value_col2)).ljust(35)+("{}".format(value_col3)).ljust(35))

      elif len(ap_excel_names) - ap_excel_names.index(ap) == 2:
        value_col1 = "({}) {}".format(ap_excel_names.index(ap)+1, ap)
        value_col2 = "({}) {}".format(ap_excel_names.index(ap)+2, ap_excel_names[ap_excel_names.index(ap)+1])

        print(("{}".format(value_col1)).ljust(35)+("{}".format(value_col2)).ljust(35))

      elif len(ap_excel_names) - ap_excel_names.index(ap) == 1:
        value_col1 = "({}) {}".format(ap_excel_names.index(ap)+1, ap)

        print(("{}".format(value_col1)).ljust(35))
      else:
        pass
    else:
      value_col1 = "({}) {}".format(ap_excel_names.index(ap)+1, ap)
      value_col2 = "({}) {}".format(ap_excel_names.index(ap)+2, ap_excel_names[ap_excel_names.index(ap)+1])
      value_col3 = "({}) {}".format(ap_excel_names.index(ap)+3, ap_excel_names[ap_excel_names.index(ap)+2])
      value_col4 = "({}) {}".format(ap_excel_names.index(ap)+4, ap_excel_names[ap_excel_names.index(ap)+3])

      print(("{}".format(value_col1)).ljust(35)+("{}".format(value_col2)).ljust(35)+("{}".format(value_col3)).ljust(35)+("{}".format(value_col4)))

configuring = False

while True:

  try:

    option = input("\n------------------\n(A) RANGE OF APs\n(B) INDEPENDENT AP\n(C) EXCEPTION AP\n(D) READY\n------------------\n\nCHOOSE AN OPTION: ")
    option = str(option).lower()

    if option == "a":
      while True:
        last_numer_range_from = False
        try:
          range_from = input("FROM : ")
          range_from = int(range_from)

          if range_from == ap_excel_names.index(ap_excel_names[-1]) + 1:
            last_numer_range_from = True

          if last_numer_range_from == False:

            while True:
              try:
                range_to = input("TO   : ")
                range_to = int(range_to)

                if range_to > range_from:
                  break

              except:
                pass
          
            break
        
        except:
          break
      
      if isinstance(range_from, int) and isinstance(range_to, int) and range_from < range_to:
        print("\n================================================================================================================================")
        print("APs SELECTED AT THE MOMENT:")

        for i in range(range_to - range_from + 1):
          aps_selected.append(ap_excel_names[range_from - 1 + i])

        aps_selected = sorted(set(aps_selected))
        print(*aps_selected, sep=" - ")

    elif option == "b":
    
      while True:
        try:
          independent_ap = input("AP to add : ")
          independent_ap = int(independent_ap)

          if independent_ap >= 1 and independent_ap <= ap_excel_names.index(ap_excel_names[-1]) + 1 and (ap_excel_names[independent_ap - 1] not in aps_selected):

            aps_selected.append(ap_excel_names[independent_ap - 1])

            continue_independent_ap = input("Continue adding independent AP? (Y/N): ")
            continue_independent_ap = (str(continue_independent_ap)).lower()

            while True:

              if continue_independent_ap != 'n' and continue_independent_ap != 'y':
                continue_independent_ap = input("Continue adding independent AP? (Y/N): ")
                continue_independent_ap = (str(continue_independent_ap)).lower()
              
              else:
                break

            if continue_independent_ap == 'n':
                break
            elif continue_independent_ap == 'y':
                pass
          else:
            print("AP Number is not in range or already added")

        except:
          print("Error adding AP number")
      
      print("\n================================================================================================================================")
      print("APs SELECTED AT THE MOMENT:")
      aps_selected = sorted(set(aps_selected))
      print(*aps_selected, sep=" - ")

    elif option == "c":

      while True:
        try:
          exception_ap = input("AP to remove : ")
          exception_ap = int(exception_ap)

          if exception_ap >= 1 and exception_ap <= ap_excel_names.index(ap_excel_names[-1]) + 1 and (ap_excel_names[exception_ap - 1] in aps_selected):
            aps_selected.remove(ap_excel_names[exception_ap - 1])

            continue_exception_ap = input("Continue removing independent AP? (Y/N): ")
            continue_exception_ap = (str(continue_exception_ap)).lower()

            while True:

              if continue_exception_ap != 'n' and continue_exception_ap != 'y':
                continue_exception_ap = input("Continue removing independent AP? (Y/N): ")
                continue_exception_ap = (str(continue_exception_ap)).lower()
              
              else:
                break

            if continue_exception_ap == 'n':
                break
            elif continue_exception_ap == 'y':
                pass
          
          else:
            print("AP number not in range or not found in APs selected")
        except:
          print("Error removing AP number")

      print("\n================================================================================================================================")
      print("APs SELECTED AT THE MOMENT:")
      aps_selected = sorted(set(aps_selected))
      print(*aps_selected, sep=" - ")


    elif option == "d":
      print("\n================================================================================================================================")
      print("APs SELECTED AT THE MOMENT:")
      aps_selected = sorted(set(aps_selected))
      print(*aps_selected, sep=" - ")
      print("")

      while True:
        try:
          request_finish = input("Are you ready to configure those APs? (Y/N): ")
          request_finish = (str(request_finish)).lower()

          while True:

            if request_finish != 'n' and request_finish != 'y':
                request_finish = input("Are you ready to configure those APs? (Y/N): ")
                request_finish = (str(request_finish)).lower()
              
            else:
                break

          if request_finish == 'n':
            break
          elif request_finish == 'y':
            break

        except:
          pass
      
      if request_finish == 'y':
        configuring = True
        break
                 
    else:
      print("\nSELECT A, B, C or D")
      
  except:
    break
    

# UPDATE OF APs' PARAMETERS

updated_devices = []

if configuring == True:

  print("\n\n=========================================\n================ SUMMARY ================\n")

  all_macs = list(mac_devices.values())
  url_rest_setting = "https://{}:{}/api/s/default/rest/setting".format(gateway["ip"], gateway["port"])
  response_rest_setting = session.get(url_rest_setting, headers=headers, verify=False)

  if response_rest_setting.status_code == 200:
    data_rest_setting = (response_rest_setting.json())['data']

    key_global_ap = "global_ap"
    id_global_ap = ""
    
    key_radio_ai = "radio_ai"
    id_radio_ai = ""

    for i in data_rest_setting:
      if i["key"] == key_global_ap:
        id_global_ap = i["_id"]
      if i["key"] == key_radio_ai:
        id_radio_ai = i["_id"]
    
    if id_global_ap != "" and id_radio_ai != "":

      # GLOBAL AP EXCEPTION FOR ALL APs
      url_put_rest_setting = "https://{}:{}/api/s/default/rest/setting/{}/{}".format(gateway["ip"], gateway["port"], key_global_ap, id_global_ap)
      payload_rest_setting = json.dumps({
        "ap_exclusions": all_macs
      })
      response_rest_setting = session.put(url_put_rest_setting, headers=headers, data=payload_rest_setting)

      # DISABLING NIGHTLY CHANNEL OPTIMIZATION
      url_disabling_nightly_channel_optimization = "https://{}:{}/api/s/default/rest/setting/{}/{}".format(gateway["ip"], gateway["port"], key_radio_ai, id_radio_ai)
      payload_disabling_channel_optimization = json.dumps({
        "enabled": False
      })
      response_disabling_channel_optimization = session.put(url_disabling_nightly_channel_optimization, headers=headers, data=payload_disabling_channel_optimization)

      if response_rest_setting.status_code == 200 and response_disabling_channel_optimization.status_code == 200:

        for ap in dict_parameters:
          if ap["NAME"] in aps_selected:

            try:
              url_update = "https://{}:{}/api/s/default/rest/device/{}".format(gateway["ip"], gateway["port"], id_devices[ap["NAME"]])

              mesh = False
              if ap["MESH"] != "No":
                mesh = True

              if len(wifi_names[ap["NAME"]]) == 2:

                payload = json.dumps({
                  "ip": ap["IP"],
                  "config_network": {
                    "type": "static",
                    "ip": ap["IP"],
                    "netmask": ap["MASK"],
                    "gateway": ap["GATEWAY"],
                    "dns1": "8.8.8.8",
                    "dns2": "8.8.4.4",
                    "dnssuffix": "",
                    "bonding_enabled": False
                  },
                  "mesh_sta_vap_enabled": mesh,
                  "radio_table": [
                    {
                      "name": wifi_names[ap["NAME"]][0],
                      "ht": "{}".format(ap["CH WIDTH 2.4"]),
                      "channel": "{}".format(ap["CH 2.4"]),
                      "tx_power_mode": "{}".format(ap["TX MODE 2.4"].lower()),
                      "vwire_enabled": False,
                      "min_rssi_enabled": True,
                      "min_rssi": ap["RSSI 2.4"],
                      "hard_noise_floor_enabled": False,
                    },
                    {
                      "name": wifi_names[ap["NAME"]][1],
                      "ht": "{}".format(ap["CH WIDTH 5.0"]),
                      "channel": "{}".format(ap["CH 5.0"]),
                      "tx_power_mode": "{}".format(ap["TX MODE 5.0"].lower()),
                      "vwire_enabled": False,
                      "min_rssi_enabled": True,
                      "min_rssi": ap["RSSI 5.0"],
                      "hard_noise_floor_enabled": False,
                    }
                  ]
                })
              
              elif len(wifi_names[ap["NAME"]]) == 1:

                payload = json.dumps({
                  "ip": ap["IP"],
                  "config_network": {
                    "type": "static",
                    "ip": ap["IP"],
                    "netmask": ap["MASK"],
                    "gateway": ap["GATEWAY"],
                    "dns1": "8.8.8.8",
                    "dns2": "8.8.4.4",
                    "dnssuffix": "",
                    "bonding_enabled": False
                  },
                  "mesh_sta_vap_enabled": mesh,
                  "radio_table": [
                    {
                      "name": wifi_names[ap["NAME"]][0],
                      "vwire_enabled": False,
                      "hard_noise_floor_enabled": False,
                      "channel": "{}".format(ap["CH 2.4"]),
                      "ht": "{}".format(ap["CH WIDTH 2.4"]),
                      "tx_power_mode": "{}".format(ap["TX MODE 2.4"].lower()),
                      "min_rssi_enabled": True,
                      "min_rssi": ap["RSSI 2.4"],
                      "vwire_enabled": mesh
                    }
                  ]
                })
              
              else:

                payload = json.dumps({
                  "mesh_sta_vap_enabled": mesh,
                  "radio_table": [
                    {
                      "min_rssi_enabled": True,
                      "vwire_enabled": mesh
                    }
                  ]
                })

              response = session.put(url_update, headers=headers, data=payload)
              updated_devices.append(ap["NAME"])

              print("* Successful Update: {}".format(ap["NAME"]))

            except:
              print("- Error found: {} not configured".format(ap["NAME"]))

        # RESULTS PRINTED
        print("\n=========================================\n======= APs UPDATED CONFIGURATION =======\n")

        updated_devices = sorted(updated_devices)

        for device in updated_devices:
          url_device = "https://{}:{}/api/s/default/stat/device/{}".format(gateway["ip"], gateway["port"],mac_devices[device])
          response_device = session.get(url_device, headers=headers, verify=False)
          data_device = (response_device.json())['data']

          print(f"DEVICE: {device}")

          if data_device[0]['state'] == 1:
            print('- State:               online')
          else:
            print('- State:               offline')
          print(f"- MAC:                 {data_device[0]['mac']}")
          print(f"- IP:                  {data_device[0]['config_network']['ip']}")
          print(f"- NETMASK:             {data_device[0]['config_network']['netmask']}")
          print(f"- GATEWAY:             {data_device[0]['config_network']['gateway']}")
          print(f"- DHCP or Static:      {data_device[0]['config_network']['type']}")
          print(f"- DNS:                 {data_device[0]['config_network']['dns1']}")
          print("- 2.4GHz Parameters:")
          print(f"  * Channel:           {data_device[0]['radio_table'][0]['channel']}")
          print(f"  * RSSI:              {data_device[0]['radio_table'][0]['min_rssi']}dBm")
          print(f"  * Power Transmit:    {data_device[0]['radio_table'][0]['tx_power_mode']}")
          print("- 5.0GHz Parameters:")
          print(f"  * Channel:           {data_device[0]['radio_table'][1]['channel']}")
          print(f"  * RSSI:              {data_device[0]['radio_table'][1]['min_rssi']}dBm")
          print(f"  * Power Transmit:    {data_device[0]['radio_table'][1]['tx_power_mode']}\n")
          print("----------------------------------------\n")
      
      else:
        print("There was an error in Global AP Exclusions or Disabling Channel Optimization")

    else:
      print("Error capturing ID for Global AP or Nightly Channel Optimization")
  
  else:
    print("Controller Error Connection")
