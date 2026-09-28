import urllib.request
import re

try:
    resp = urllib.request.urlopen('https://europa.eu/eures/portal/jv-se/main-TD4BKMNS.js')
    js = resp.read().decode('utf-8')
    print('Length:', len(js))
    urls = re.findall(r'https?://[a-zA-Z0-9./_-]+api[a-zA-Z0-9./_-]+', js)
    paths = re.findall(r'"(/[a-zA-Z0-9./_-]+api[a-zA-Z0-9./_-]+)"', js)
    print('URLs:', set(urls))
    print('Paths:', set(paths))
    
    jv_paths = re.findall(r'"(/eures-apps/[a-zA-Z0-9./_-]+)"', js)
    if len(jv_paths) > 0:
        print('JV Paths:', set(jv_paths))
        
except Exception as e:
    print('Failed:', e)
