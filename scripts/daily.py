"""Quota-aware, fail-closed catalogue revalidation. No AI API or paid service required.
Official provider pages are checked in rotating batches; HTTP reachability does not
establish rights, region availability or playback. Reviewed season/film candidates
require source evidence before API metadata validation. Discovery uploads stay in quarantine.
"""
import argparse, json, os, time, urllib.request, urllib.error, urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone, timedelta
ROOT=Path(__file__).resolve().parents[1]
def read(p,default):
 f=ROOT/p
 return json.loads(f.read_text()) if f.exists() else default
def write(p,data):
 f=ROOT/p;f.parent.mkdir(parents=True,exist_ok=True);temp=f.with_suffix('.tmp');temp.write_text(json.dumps(data,indent=2,ensure_ascii=False));temp.replace(f)
def http(url,method='GET'):
 # Only official known providers and their documented APIs. Never arbitrary candidate URLs.
 host=urllib.parse.urlparse(url).hostname
 if host not in {'www.googleapis.com','www.youtube.com','www.netflix.com','www.crunchyroll.com'}:raise ValueError('Non-allowlisted host')
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AniLoveIndia/1.0 (+mailto:niteshpatel7479@gmail.com)'},method=method),timeout=12) as r:return r.status,r.read().decode()
  except urllib.error.HTTPError as e:
   if e.code not in {429,500,502,503,504}:return e.code,''
   if attempt==2:return e.code,''
  except (urllib.error.URLError,TimeoutError):
   if attempt==2:return 0,''
  time.sleep(2**attempt)
 return 0,''
def yt(resource,params,key):
 params={**params,'key':key};code,body=http('https://www.googleapis.com/youtube/v3/'+resource+'?'+urllib.parse.urlencode(params))
 if code!=200:raise RuntimeError('YouTube Data API request failed with status '+str(code))
 return json.loads(body)
def eligible(v,channel,minimum=300):
 status=v.get('status',{});content=v.get('contentDetails',{});regions=content.get('regionRestriction',{})
 if status.get('privacyStatus')!='public' or status.get('embeddable') is not True:return False
 if v.get('snippet',{}).get('channelId')!=channel:return False
 if 'IN' in regions.get('blocked',[]) or ('allowed'in regions and 'IN'not in regions['allowed']):return False
 if content.get('contentRating',{}).get('ytRating')=='ytAgeRestricted':return False
 import re
 m=re.fullmatch(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',content.get('duration',''))
 if not m:return False
 sec=int(m[1]or 0)*3600+int(m[2]or 0)*60+int(m[3]or 0)
 return sec>=minimum

def validate_candidate(c,key,channels):
 errors=[]
 if c.get('channel_id') not in channels:errors.append('Channel is not reviewed and allowlisted')
 for field in ['authorization_evidence_url','metadata_source_url','audio_language','expected_episode_numbers']:
  if not c.get(field):errors.append('Missing '+field)
 ep=c.get('episodes',[]);expected=c.get('expected_episode_numbers',[])
 if not expected or len(expected)!=len(set(expected)):errors.append('Expected order missing or duplicated')
 if [x.get('number')for x in ep]!=expected:errors.append('Episode order does not match expected list')
 ids=[x.get('video_id')for x in ep]
 if len(ids)!=len(set(ids))or any(not x for x in ids):errors.append('Missing or duplicate video IDs')
 if errors:return False,errors
 if not key:return False,['YouTube Data API key missing']
 # Entire candidate must pass; partial playlists never become complete.
 videos={}
 for i in range(0,len(ids),50):
  response=yt('videos',{'part':'snippet,status,contentDetails','id':','.join(ids[i:i+50])},key)
  videos.update({v['id']:v for v in response.get('items',[])})
 for video in ids:
  if video not in videos or not eligible(videos[video],c['channel_id'],c.get('minimum_runtime_seconds',300)):errors.append('Video failed metadata/public/region/embedding gate: '+video)
 # API checks alone never qualify as playback verification.
 if not c.get('india_playback_review',{}).get('verified_at')or not c.get('india_playback_review',{}).get('reviewer'):errors.append('Actual India playback review missing')
 return not errors,errors

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');args=parser.parse_args()
 now=datetime.now(timezone.utc);catalogue=read('data/catalogue.json',[]);old=read('data/status.json',{});key=os.environ.get('YOUTUBE_API_KEY');channels=read('data/channels.json',[])
 status={'scheduler_active':os.environ.get('GITHUB_ACTIONS')=='true','last_run':now.isoformat(),'schedule':'09:00 Asia/Kolkata (03:30 UTC; scheduler may delay)','state':'Offline test passed' if args.offline else 'Checks completed with publication gates','added':{},'changed_availability':[],'link_checks':[],'blog':{'published':0,'skipped':'No new reviewed source-backed topic; no AI generation required or attempted.'},'errors':[],'next_scheduled_run':None}
 if status['scheduler_active']:
  nxt=now.replace(hour=3,minute=30,second=0,microsecond=0)
  if nxt<=now:nxt+=timedelta(days=1)
  status['next_scheduled_run']=nxt.isoformat()
 if not key:status['errors'].append('YouTube Data API key missing: upload discovery and episode validation disabled.')
 if args.offline:
  print(json.dumps({'offline_test':'passed','titles':len(catalogue),'scheduler_active':False,'missing_api_key':not bool(key)}));return
 # Rotating batches keep network and API use bounded. Search is never used for automated publishing.
 offset=old.get('cursor',0)%max(1,len(catalogue));batch=(catalogue+catalogue)[offset:offset+5]
 for t in batch:
  code,_=http(t['watch_url'],method='HEAD');record={'title_id':t['id'],'status':code,'checked_at':now.isoformat(),'meaning':'HTTP reachability only; playback and India entitlement unverified'}
  status['link_checks'].append(record)
  if code in [404,410]:
   if t['availability']!='unverified':status['changed_availability'].append(t['id'])
   t['availability']='unverified';t['region_note']='Official page returned missing; current legal route requires review.'
  elif code!=200:status['errors'].append('Provider link not verified for '+t['id']+' (HTTP '+str(code)+')')
 status['cursor']=(offset+len(batch))%max(1,len(catalogue))
 # Only reviewed channel IDs are queried. New uploads remain private repository candidates.
 queue=read('data/discovery-queue.json',[]);seen={x['video_id']for x in queue};active_channels={c['channel_id']for c in channels if c.get('identity_reviewed')and c.get('identity_evidence_url')}
 if key:
  for channel in channels:
   if channel.get('channel_id')not in active_channels:continue
   try:
    info=yt('channels',{'part':'contentDetails','id':channel['channel_id']},key).get('items',[])
    if not info:continue
    uploads=info[0]['contentDetails']['relatedPlaylists']['uploads']
    items=yt('playlistItems',{'part':'snippet,contentDetails','playlistId':uploads,'maxResults':10},key).get('items',[])
    for v in items:
     video_id=v['contentDetails']['videoId']
     if video_id not in seen:queue.append({'video_id':video_id,'channel_id':channel['channel_id'],'title':v['snippet']['title'],'state':'needs-human-full-length-and-authorization-review','found_at':now.isoformat()});seen.add(video_id)
   except Exception:status['errors'].append('Upload discovery failed for reviewed channel '+channel['channel_id'])
 for c in read('data/candidates.json',[]):
  try:ok,errors=validate_candidate(c,key,active_channels)
  except Exception:ok,errors=False,['Candidate API validation failed']
  c['validation']={'at':now.isoformat(),'passed':ok,'errors':errors}
  if not ok:status['errors'].append('Candidate '+str(c.get('id','unknown'))+' blocked: '+'; '.join(errors));continue
  # Candidate must reference an existing reviewed title; edition identity is explicit.
  title=next((t for t in catalogue if t['id']==c.get('title_id')),None)
  if not title:status['errors'].append('Unknown parent title for candidate');continue
  edition_id=c['id'];season=next((s for s in title['seasons']if s['id']==edition_id),None)
  record={**c,'verified_complete':True,'last_checked':now.isoformat()}
  if season:season.clear();season.update(record)
  else:title['seasons'].append(record);status['added'][title['category']]=status['added'].get(title['category'],0)+1
 # Existing playable editions are never left verified after an API failure.
 for title in catalogue:
  for season in title['seasons']:
   try:ok,errors=validate_candidate(season,key,active_channels)
   except Exception:ok,errors=False,['Recheck failed']
   season['verified_complete']=ok
   if not ok:season['verification_errors']=errors
 write('data/catalogue.json',catalogue);write('data/discovery-queue.json',queue);write('data/status.json',status)
 history=read('data/run-history.json',[]);history.append(status);write('data/run-history.json',history[-30:])
 print(json.dumps({'checks':len(status['link_checks']),'errors':len(status['errors']),'added':status['added'],'scheduler_active':status['scheduler_active']}))
if __name__=='__main__':main()
