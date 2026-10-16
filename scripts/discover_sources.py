import urllib.request,re,json,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
urls={'tms':'https://tmsanime.com/anime-on-tms-official-channel','muse-playlists':'https://www.youtube.com/@MuseAsia/playlists','muse-india-playlists':'https://www.youtube.com/@MuseIndiaChannel/playlists','kbs':'https://kbsworld.kbs.co.kr/vod/latest_episode.php','korean-archive':'https://eng.koreafilm.or.kr/'}
def scan(item):
 name,u=item
 try:
  s=urllib.request.urlopen(u,timeout=25).read().decode();(ROOT/'research'/f'{name}.html').write_text(s)
  out={'name':name,'url':u,'youtube_links':list(dict.fromkeys(re.findall(r'https?://(?:www\.)?(?:youtube\.com|youtu\.be)/[^"<>\s]+',s)))}
  m=re.search(r'var ytInitialData = (\{.*?\});',s)
  if m:
   d=json.loads(m[1]);(ROOT/'research'/f'{name}.json').write_text(json.dumps(d));out['metadata']=d.get('metadata',{});out['has_playlist_id']=len(re.findall('playlistId',s))
  return out
 except Exception as e:return {'name':name,'error':str(e)}
r=list(concurrent.futures.ThreadPoolExecutor(max_workers=5).map(scan,urls.items()));(ROOT/'research/sources.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,ensure_ascii=False)[:24000])
