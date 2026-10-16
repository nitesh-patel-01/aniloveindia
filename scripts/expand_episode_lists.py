"""Import manually collected public official-playlist entries after metadata checks.
Input: data/playlist-index.json. Verification: data/episode-verification.json.
Does not mark India playback or series/season completion verified.
"""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def key(title):
 lower=title.lower()
 if 'movie'in lower or '365'in lower:return ('movie',1)
 special=re.search(r'\(S(\d+)E(\d+)\)',title,re.I)
 if special:return int(special[1]),str(int(special[2]))
 m=re.search(r'(?:Season\s*(\d+)|(\d+)(?:st|nd|rd|th)\s*Season|\(S(\d+)|\bS(\d+)\b)',title,re.I);season=int(next(x for x in m.groups()if x))if m else 1
 # Assassination Classroom 2 uses the sequel number instead of Season 2.
 if re.search(r'ASSASSINATION CLASSROOM 2',title,re.I):season=2
 ep=re.search(r'Episode\s*(\d+[ABab]?(?:[～~–-]\d+)?)',title,re.I)
 if not ep:return None
 number=ep[1].lower().replace('～','-').replace('~','-').replace('–','-')
 number=re.sub(r'(^|-)0+(?=\d)',r'\1',number)
 return season,number
def main():
 cat=json.loads((ROOT/'data/catalogue.json').read_text());indexed=json.loads((ROOT/'data/playlist-index.json').read_text());verification=json.loads((ROOT/'data/episode-verification.json').read_text());lookup={v['id']:v for v in verification};report={};excluded=[]
 for t in cat:
  if t['category']=='anime-movies':continue
  ps=set(t.get('source_playlist_ids',[]))|{s.get('playlist_id')for s in t['seasons']};rows=[r for p in indexed if p['playlist']in ps for r in p['rows']];groups={}
  for row in rows:
   vid=row['video_id'];v=lookup.get(vid,{})
   parsed=key(v.get('title')or '')
   if not parsed or parsed[0]=='movie':continue
   if not v.get('eligible'):
    excluded.append({'title_id':t['id'],'video_id':vid,'reason':v.get('reason','Metadata check missing')});continue
   channel='UCYYhAzgWuxPauRXdPpLAX3Q'if t['provider']=='Muse India'else 'UCGbshtvS9t-8CW11W7TooQg'
   if v.get('channel_id')!=channel:continue
   season,number=parsed
   groups.setdefault(season,{})[number]={'number':number,'title':v['title'],'video_id':vid,'duration_seconds':v['seconds'],'metadata_check':'Public official playlist + uploader identity, full-length runtime, oEmbed iframe and India country metadata','india_playback':'unverified'}
  seasons=[]
  for num,eps in sorted(groups.items()):
   # Keep distinct director-cut A/B segments and multi-episode uploads.
   eps=sorted(eps.values(),key=lambda e:(int(re.match(r'\d+',e['number'])[0]),e['number']))
   old=next((s for s in t.get('source_editions',t['seasons'])if s['id'].endswith('season-'+str(num))or ('season-'+str(num)+'-'in s['id'])),None)
   if t['id']=='re-zero'and num==1:old=next(s for s in t['seasons']if 'directors' in s['id'])
   if t['id']=='jojos-bizarre-adventure':
    old=next((s for s in t.get('source_editions',t['seasons'])if ['phantom','stardust','diamond','golden'][num-1]in s['id']),None)if num<=4 else None
   base=dict(old or t['seasons'][0]);base.update(id=old['id']if old else t['id']+'-season-'+str(num),label=old.get('label')if old else 'Season '+str(num),episodes=eps,embed_checked=True,verified_complete=False,completion_note=str(len(eps))+' checked official full-length uploads listed. India playback and full-season completion are not certified.',last_checked='2026-10-16',listed_uploads=len(eps));seasons.append(base)
  if seasons:
   found={s['id']for s in seasons};seasons.extend(s for s in t['seasons']if s['id']not in found);t['seasons']=seasons
  report[t['id']]=sum(len(s['episodes'])for s in t['seasons'])
 (ROOT/'data/catalogue.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2));(ROOT/'data/episode-import-report.json').write_text(json.dumps({'listed':report,'excluded':excluded},ensure_ascii=False,indent=2));print(json.dumps(report))
if __name__=='__main__':main()
