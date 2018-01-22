import json
from urllib import request,parse

#url = "http://172.27.10.45/"
username="admin"
password="zabbix"
url = "http://172.27.10.45/"
header = {"Content-Type": "application/json"}
reurl = url + "api_jsonrpc.php"

def get_login():
    data = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": username,
            "password": password
         },
        "id": 1,
        }
    value = json.dumps(data).encode("utf-8")
    req = request.Request(reurl,headers=header,data=value)
    try:
        result = request.urlopen(req)
    except Exception as e:
        print(e)
    else:
        page = result.read().decode("utf-8")
        page = json.loads(page)
        return page

def get_auth():
    with open("./auth.txt",'w') as f:
        f.write(get_login().get("result"))
        f.close()

def main():
    get_auth()

if __name__ == "__main__":
    main()
