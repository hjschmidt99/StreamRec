import sys
import os
import json
import traceback
import clipboard
import HandleM3u 
from pyjsonq import JsonQ

url = sys.argv[1] if len(sys.argv) > 1 else clipboard.paste()
m3u = HandleM3u.decodeM3u(url)
q = JsonQ(data = m3u)

p1 = "BANDWIDTH"
res = q.at("VIDEO").where(p1, "<", 5000000).sort_by(p1).last()
#print(json.dumps(res, indent=4))

x = res["INDEX"]
print(x)

#input("...")
