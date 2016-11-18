import argparse
import urllib.request
import json

mainParser = argparse.ArgumentParser()
mainParser.add_argument('host', help="Сервер Cache")
mainParser.add_argument('namespace', help="namespace")
    
results = mainParser.parse_args()
kwargs = dict(results._get_kwargs())
host = kwargs.pop('host')
namespace = kwargs.pop('namespace')
filenames_file = open("cacheclasses.txt","r")
filenames = filenames_file.read().split('\n')
for filename in filenames:
    req = urllib.request.Request(url='http://' + host + ':57772/csp/sys/dev/namespaces/' + namespace + '/files/' + filename,method='GET')
    res = urllib.request.urlopen(req, timeout=5)
    res_body = res.read()
    f = open(filename,'w')
    j = json.loads(res_body.decode('cp1251'))
    f.write(j['content'])
    f.close()
exit(0)