import json
from urllib import request,parse

#url = "http://172.27.10.45/"
username="admin"
password="zabbix"
url = "http://172.27.10.45/"
header = {"Content-Type": "application/json"}
reurl = url + "api_jsonrpc.php"

GA=["BJ-Server","hk-server","mysql_slave","SIN_server","Tokyo_server","Ucloud","Zabbix servers"]

def get_status(Group):
    data = {
            "jsonrpc": "2.0",
            "method" : "hostgroup.get",
            "params":{
             "output":["groupid","name"],
             "selectHosts":["groupname",
                  "host"],
            "filter": {
            "name": [
                Group,
            ]
        }
          },

  "auth": "3019262bbcf1f6f253ea277ddda0ef9e",
    "id": 2
}   
    req = request.Request(reurl,headers=header,data=json.dumps(data).encode("utf-8"))
    try:
        result = request.urlopen(req)
    except Exception as e:
        print( e)
    else:
        page = result.read().decode("utf-8")
        page = json.loads(page)
        return page      

def Tok_group(page):
    for group in page:
        group = page.get("result")[0].get("name")
        return group
def Tok_ser(page):
        hosts = page.get("result")[0].get("hosts")
        for host in hosts:
            print(host["host"])

def main():
    print(Tok_group(get_status(Group)))
    Tok_ser(get_status(Group))
#get_status(get_login())
if __name__ == "__main__":
    for Group in GA:
        main()
