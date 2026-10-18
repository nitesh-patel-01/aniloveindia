"""Read public watch-page metadata and YouTube oEmbed. Never request video streams."""
import urllib.request,urllib.parse,urllib.error,json,re,concurrent.futures,time
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'data/episode-verification.json'
def check(vid):
 result={'id':vid,'eligible':False,'checked_at':datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat()}
 try:
  page=urllib.request.urlopen('https://www.youtube.com/watch?v='+vid,timeout=20).read().decode();match=re.search(r'ytInitialPlayerResponse\s*=\s*(\{.*?\});',page)
  if not match:result['reason']='Watch metadata missing';return result
  p=json.loads(match[1]);d=p.get('videoDetails',{});mf=p.get('microformat',{}).get('playerMicroformatRenderer',{});channel=d.get('channelId');seconds=int(d.get('lengthSeconds',0));countries=mf.get('availableCountries',[])
  result.update(author=d.get('author'),playlist_ids=list(dict.fromkeys(re.findall(r'list=(PL[A-Za-z0-9_-]+)',d.get('shortDescription','')))),caption_languages=[c.get('languageCode')for c in p.get('captions',{}).get('playerCaptionsTracklistRenderer',{}).get('captionTracks',[])],title=d.get('title'),channel_id=channel,seconds=seconds,india_in_country_metadata='IN'in countries,actual_india_playback='unverified')
  if not channel:
   result.update(reason='Uploader identity metadata unavailable',player_status=p.get('playabilityStatus',{}).get('status'),player_reason=p.get('playabilityStatus',{}).get('reason'));return result
  if channel not in {c['channel_id']for c in json.loads((ROOT/'data/channels.json').read_text())if c.get('identity_reviewed')}:result['reason']='Uploader not approved';return result
  status=p.get('playabilityStatus',{}); reason=str(status).lower()
  result.update(player_status=status.get('status'),player_reason=status.get('reason'),publish_date=mf.get('publishDate'),is_unlisted=mf.get('isUnlisted',False),is_live=bool(d.get('isLiveContent')),source_url='https://www.youtube.com/watch?v='+vid)
  if d.get('isLiveContent') or d.get('isUpcoming') or mf.get('isUnlisted') or any(x in reason for x in ['age-restricted','confirm your age','members-only','members only','join this channel','purchase','rental','paid video','premiere will begin']):result['reason']='Restricted, unlisted, upcoming or live upload';return result
  if status.get('status') not in ('OK','UNPLAYABLE'):result['reason']='Public player status could not be verified';return result
  if status.get('status')=='UNPLAYABLE' and not any(x in reason for x in ['country','region','location']):result['reason']='Unplayable for an unverified reason';return result
  if seconds<300 or d.get('isPrivate')or not mf.get('embed')or 'IN'not in countries:result['reason']='Runtime, privacy, iframe or India metadata failed';return result
  url='https://www.youtube.com/oembed?format=json&url='+urllib.parse.quote('https://www.youtube.com/watch?v='+vid,safe='')
  embed=json.load(urllib.request.urlopen(url,timeout=15))
  if '<iframe'not in embed.get('html','')or embed.get('author_name')!=d.get('author'):result['reason']='oEmbed failed';return result
  result.update(eligible=True,oembed=True)
 except urllib.error.HTTPError as e:result['reason']='HTTP '+str(e.code)
 except Exception as e:result['reason']=type(e).__name__
 return result
if __name__=='__main__':
 indexed=json.loads((ROOT/'data/playlist-index.json').read_text());ids=list(dict.fromkeys(r['video_id']for p in indexed for r in p['rows']));old=json.loads(PATH.read_text())if PATH.exists()else [];results={r['id']:r for r in old};todo=[v for v in ids if v not in results]
 print(json.dumps({'to_check':len(todo),'cached':len(results)}),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=8)as pool:
  for i,r in enumerate(pool.map(check,todo)):
   results[r['id']]=r
   if (i+1)%20==0:
    PATH.write_text(json.dumps(list(results.values()),ensure_ascii=False,indent=2));print(json.dumps({'checked':i+1,'eligible':sum(x.get('eligible',False)for x in results.values())}),flush=True)
 PATH.write_text(json.dumps(list(results.values()),ensure_ascii=False,indent=2));print(json.dumps({'total':len(results),'eligible':sum(x.get('eligible',False)for x in results.values())}),flush=True)
