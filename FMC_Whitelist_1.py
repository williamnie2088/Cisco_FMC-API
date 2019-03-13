import datetime
import json
import requests
import sys

action = sys.argv[1]
ipaddr = sys.argv[2]
if len(sys.argv) < 2:
 print ("action and ipaddr argument required")
 exit()

username = "Username_for_FMC"
password = 'password'
serverIP = "FMC_IP"
objid = "login_id"


###get auth token
url = "https://%s/api/fmc_platform/v1/auth/generatetoken" % serverIP
response = requests.post(url, auth=(username,password), verify=False) #verify=False ignoring the cert and adding all the message spitting our from the request to 'response'
authtoken = response.headers['X-auth-access-token'] #only get the portion where  it has the 'X-auth-access-token'

#### GET current whitelist
url = "https://%s/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/object/networkgroups/%s" % (serverIP, objid)
headers = {
   'x-auth-access-token': authtoken,
    'Content-Type': "application/json", #telling the system we're using json for inputting the body
   'cache-control': "no-cache"
   }

response = requests.get(url, headers=headers, verify=False)
result = response.json()
iplist = result['literals']
name = result['name']
new_iplist = []

if action == 'del':
 print ("del")
 for element in iplist:
   if ipaddr not in element["value"]:
       new_iplist.append(element)
elif action == 'get' :
    print (iplist)
    exit()
elif action == 'add':
 new_iplist = iplist
 element = {
                "type": "Host",
                "value": ipaddr
            }
 new_iplist.append(element) #append is adding the new element in the list

### PUT new whitelist
json_data = {
 "id": objid,
 "name": name,
 "literals": new_iplist
}
response = requests.put(url, data=json.dumps(json_data), headers=headers, verify=False) #json.dumps to input the data in jason format

### deploy
nowtime = int(1000 * datetime.datetime.now().timestamp())
deploy_data = {
    'type': 'DeploymentRequest',
    'forceDeploy': True,
    'ignoreWarning': True,
    'version': nowtime,
    "deviceList": [
                    "65dfc774-ab2c-11e6-8b25-db1e2c9d2853",
                    "776907f6-ab2e-11e6-a498-f073f058190f"
                  ]
}

deploy_url = "https://%s/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/deployment/deploymentrequests" % (serverIP)
response = requests.post(deploy_url, data=json.dumps(deploy_data), headers=headers, verify=False)

## put = modify change; get = gets data; post = create new; del = delete object
