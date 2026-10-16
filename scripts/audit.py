import json,re,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse,unquote
root=Path(__file__).resolve().parents[1];dist=root/'dist';errors=[];titles=set();count=0
for p in dist.rglob('*.html'):
 s=p.read_text();count+=1
 title=re.search(r'<title>(.*?)</title>',s)
 if not title:errors.append(str(p)+' missing title')
 elif title[1] in titles and '404' not in str(p):errors.append('Duplicate title '+title[1])
 else:titles.add(title[1])
 for required in ['name="description"','rel="canonical"','<h1','<main','name="viewport"','class="skip"']:
  if required not in s:errors.append(str(p)+' missing '+required)
 for schema in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s):json.loads(schema)
 for href in re.findall(r'(?:href|src)="(/[^"#?]*)',s):
  target=dist/unquote(href).lstrip('/')
  if href.endswith('/'):target=target/'index.html'
  if not target.exists():errors.append(str(p)+' broken '+href)
 if ('netflix.com' in s.lower() or 'crunchyroll.com' in s.lower()):errors.append('Removed external provider still present')
 if '<select' in s:errors.append('Complex filter still present')
ET.parse(dist/'sitemap.xml')
for t in json.loads((root/'data/catalogue.json').read_text()):
 if urlparse(t['watch_url']).hostname!='www.youtube.com':errors.append('Non-YouTube source')
 for season in t['seasons']:
  if season.get('verified_complete') and not season.get('india_playback_review'):errors.append('Missing playback evidence')
print(json.dumps({'html_pages':count,'errors':errors},indent=2))
if errors:raise SystemExit(1)
