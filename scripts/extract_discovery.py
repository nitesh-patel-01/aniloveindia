import json,re,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def walk(x,key):
 if isinstance(x,dict):
  for k,v in x.items():
   if k==key:yield v
   else:yield from walk(v,key)
 elif isinstance(x,list):
  for v in x:yield from walk(v,key)
def discover(n):
 d=json.loads((ROOT/'research'/f'{n}.json').read_text());ch=d.get('metadata',{}).get('channelMetadataRenderer',{});out=[]
 for v in walk(d,'lockupViewModel'):
  if v.get('contentType')not in ['LOCKUP_CONTENT_TYPE_PLAYLIST','LOCKUP_CONTENT_TYPE_VIDEO']:continue
  title=v.get('metadata',{}).get('lockupMetadataViewModel',{}).get('title',{}).get('content','');ep=next(walk(v.get('itemPlayback',{}),'watchEndpoint'),{});out.append({'title':title,('playlist_id' if v.get('contentType')=='LOCKUP_CONTENT_TYPE_PLAYLIST' else 'video_id'):v['contentId'],'first_video':ep.get('videoId'),'channel_id':ch.get('externalId'),'provider':ch.get('title')})
 for v in walk(d,'videoRenderer'):
  title=''.join(r.get('text','')for r in v.get('title',{}).get('runs',[]));out.append({'title':title,'video_id':v.get('videoId'),'channel_id':ch.get('externalId'),'provider':ch.get('title'),'runtime_label':v.get('lengthText',{}).get('simpleText')})
 return out
if __name__=="__main__":
 r={}
 for n in ['muse-playlists','muse-india-playlists','kbs-playlists','korean-film-videos','shemaroo-videos','tms-playlists']:
  r[n]=discover(n)
 (ROOT/'data/discovered-sources.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
 for k,v in r.items():print(k,json.dumps(v,ensure_ascii=False))
