import requests, re
r = requests.get('https://bookface-static.ycombinator.com/vite/assets/ycdc-new-YnN9h2vH.js', timeout=5)
endpoints = re.findall(r'[\'\"\`](/[a-zA-Z0-9/\-_]+)[\'\"\`]', r.text)
print('Endpoints:', list(set(endpoints))[:50])
