import requests, re
r = requests.get('https://www.wayup.com/cdn/static/_next/static/chunks/pages/_app-9a64f998c9870a29.js')
print(re.findall(r'\"([^\"]*?api/v[^\"]*?)\"', r.text))
