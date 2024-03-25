import sys
import os
import json
import traceback
import clipboard
import HandleM3u 
import jmespath as jp

url = sys.argv[1] if len(sys.argv) > 1 else clipboard.paste()
m3u = HandleM3u.decodeM3u(url)
#print(json.dumps(m3u, indent=4))

x = jp.search("VIDEO[?BANDWIDTH < `8000000`] | sort_by(@, &BANDWIDTH)[-1].INDEX", m3u)
print(x)
#print(json.dumps(x, indent=4))

#input("...")
