import json,re,urllib.request,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def walk(x,key):
 if isinstance(x,dict):
  for k,v in x.items():
   if k==key:yield v
   else:yield from walk(v,key)
 elif isinstance(x,list):
  for v in x:yield from walk(v,key)
def get(pid):
 p=ROOT/'research'/('playlist-'+pid+'.json')
 if p.exists():return json.loads(p.read_text())
 try:
  s=urllib.request.urlopen('https://www.youtube.com/playlist?list='+pid,timeout=22).read().decode();m=re.search(r'var ytInitialData = (\{.*?\});',s)
  if not m:return {'playlist_id':pid,'error':'No public playlist metadata'}
  d=json.loads(m[1]);md=d.get('metadata',{}).get('playlistMetadataRenderer',{});rows=[]
  for v in walk(d,'playlistVideoRenderer'):
   title=''.join(r.get('text','')for r in v.get('title',{}).get('runs',[]));by=v.get('shortBylineText',{}).get('runs',[{}])[0];channel=by.get('navigationEndpoint',{}).get('browseEndpoint',{}).get('browseId');rows.append({'video_id':v.get('videoId'),'title':title,'runtime_label':v.get('lengthText',{}).get('simpleText'),'runtime_seconds':int(v.get('lengthSeconds',0)),'channel_id':channel,'author':by.get('text'),'playable':v.get('isPlayable')})
  out={'playlist_id':pid,'title':md.get('title'),'description':md.get('description'),'rows':rows,'alerts':d.get('alerts',[]),'has_continuation':bool(list(walk(d.get('contents',{}),'continuationItemRenderer')))};p.write_text(json.dumps(out,ensure_ascii=False,indent=2));return out
 except Exception as e:return {'playlist_id':pid,'error':str(e)}
if __name__=='__main__':
 import html
 s=(ROOT/'research/tms.html').read_text();ids=list(dict.fromkeys(re.findall(r'list=(PL[A-Za-z0-9_-]+)',s)));ids+=['PLpm1VVK4UL16L6BF7L7_0vasF5UVKCSSw']
 data=json.loads((ROOT/'data/discovered-sources.json').read_text())
 for n in ['muse-playlists','muse-india-playlists']:
  ids += [x['playlist_id']for x in data[n]if not re.search('Highlight|Promotion|Ending|now on OTT',x['title'],re.I)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:
  results=list(pool.map(get,dict.fromkeys(ids)))
 (ROOT/'data/discovered-playlists.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print(json.dumps([{'id':r['playlist_id'],'title':r.get('title'),'videos':len(r.get('rows',[])),'error':r.get('error')}for r in results],ensure_ascii=False))
