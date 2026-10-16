"""Import only checked official full uploads; preserve catalogue and source attribution."""
import json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def slug(s):return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip('-')
movies=['Mera Badla Revenge 2','Ab Tak Chappan 2','Joshila','The Real Story of Terror Barsati Gang','Vardaan Devi Maa Ka','Aur Ek Tezz Khiladi','Psycho Shankara','Shabri','Naag Bhoomi','Jwalamukhi: Man With Fire','Robo Chacha','Zulm Ka Rakshak','Amba','Pareshaan Parinda','Deewane Huye Paagal','Haunted Villa Lonavala','Chaand Kaa Tukdaa','No Smoking','Ugly Aur Pagli','Himmatwala','Bahurani','Saanwariya - Khatu Shyam Ji Ki Amar Gatha','Lovesongs: Yesterday, Today & Tomorrow','Haathi Mere Saathi','Aan - Men at Work','IPC 376','International Rowdy','Stalker','Beqabu','Angaaray']
sm=dict(zip('WCb6mFAAZ_4 n0z4PeLZVYI 545w-Imumr8 CVBtVYCJTrY a3Zd1Zip_kk uUEyFBR1_u8 -bUAJLJ9wIE MvQRlmRKrsw untflYxWYM4 fv_WxoR2YwY PSenU7ezoos yya0eDqCn9k cOj2o_HaHZA IO-Q85xwptY Mwhra8KI8UU o4AiYMQkEyQ TK_0Lo-XSeo FWg957n9r1s fWgAqbU1Ppo iSp4b9C-tPY 0o08jIV497A QpRonzSVWtw V4ZHeM6Z1VM 9BJwT9OYQ9Y _upm7eWo-4A RD9EmSTsWSE l9gnxmsnC6U Kmb0x3NsfPw EGGBKaDwplY h_k5IczFLjA'.split(),movies))
def drama_name(s):
 if 'Who Are You' in s:return 'Who Are You: School 2015'
 s=re.sub(r'^\[(?:Full(?: EP\.\d+)?|ENG)\]\s*','',s,flags=re.I)
 s=re.split(r'\s*\||\s*[–-]\s*Ep\.?|\s+EP\.?\s*\d',s,flags=re.I)[0].strip()
 return re.sub(r'\s*\[SUB[^]]*\]','',s,flags=re.I).strip()
if __name__=='__main__':
 data=json.loads((ROOT/'data/catalogue.json').read_text());byid={t['id']:t for t in data};existing={e['video_id']for t in data for s in t['seasons']for e in s['episodes']};q=json.loads((ROOT/'data/expansion-queue.json').read_text());comp={v['video_id']for v in q if v.get('kind')=='compilation'}
 for v in json.loads((ROOT/'data/expansion-verification.json').read_text()):
  if not v.get('eligible')or v['id']in existing:continue
  author=v['author'];raw=v['title'];number='full';label='Full movie';fmt='Movie';category='movies';audio='Korean';subs=['English']if 'en'in v.get('caption_languages',[])else [];country='South Korea';genre=['Cinema'];name=raw;original=raw;year=None
  if author=='KBS WORLD TV':
   if 'The Wonders of Korea' in raw:continue
   if v['seconds']<1500 or re.search(r'Part\.?\s*\d+',raw,re.I):continue
   category='k-dramas';fmt='Series';name=drama_name(raw);m=re.search(r'\bEp\.?\s*(\d+)',raw,re.I)
   if not m:continue
   number=str(int(m[1]));label='Available episodes';genre=['Drama'];subs=['English']if re.search(r'ENG',raw)or 'en'in v.get('caption_languages',[])else []
  elif author=='Anime! on TMS Official Channel':
   category='anime-movies';audio='English';country='Japan';genre=['Animation'];name=re.split(r'\s*\(\d{4}\)',raw)[0];m=re.search(r'\((\d{4})\)',raw);year=int(m[1])if m else None
  elif author in ['Muse India','Muse Asia']:
   category='anime-series';fmt='Series';audio='Japanese';country='Japan';genre=['Anime'];subs=['English']if 'English Sub'in raw or v['id']in comp else subs
   if v['id']in comp:name=re.sub(r'^【[^】]*】\s*','',raw);number='complete';label='Full-series compilation'
   else:
    m=re.search(r'Episode\s*0*(\d+)',raw,re.I)
    if not m:continue
    number=str(int(m[1]));name=re.split(r'\s+-\s+Episode',raw)[0];label='Available episodes'
  elif 'Korean Classic Film'in author:
   if v['seconds']<3600 or '/'not in raw:continue
   name=raw.split('/',1)[1].strip();name=re.split(r'\s*\(',name)[0].strip();m=re.search(r'\((\d{4})\)',raw);year=int(m[1])if m else None
  elif author=='Shemaroo Movies':
   if v['id']not in sm or v['seconds']<3600:continue
   name=sm[v['id']];audio='Hindi';country='India';genre=['Cinema']
  else:continue
  tid=slug(name);sid=tid+('-movie'if fmt=='Movie'else '-uploads');url='https://www.youtube.com/watch?v='+v['id']
  episode={'number':number,'title':raw,'video_id':v['id'],'duration_seconds':v['seconds'],'metadata_check':'Official uploader, runtime, public embed and India country metadata checked','india_playback':'unverified'}
  if tid in byid:
   t=byid[tid];s=t['seasons'][0]
   if not any(e['number']==number for e in s['episodes']):s['episodes'].append(episode);s['episodes'].sort(key=lambda e:int(e['number'])if str(e['number']).isdigit()else 10000)
   continue
  synopsis=(f'Watch {name} from {author} in the embedded YouTube player. '+('This edition is one long compilation upload; use the player timeline to move through it.'if number=='complete'else 'Choose a listed episode below. Additional episodes are included only after their source checks pass.'if fmt=='Series'else 'The full-length official upload is available below.'))
  season={'id':sid,'label':label,'audio_language':audio,'subtitle_languages':subs,'embed_checked':True,'verified_complete':False,'completion_note':'Checked official uploads. Full-season completion and actual India playback have not been certified.','last_checked':'2026-10-16','authorization_evidence_url':url,'channel_id':v['channel_id'],'episodes':[episode]}
  t={'id':tid,'title':name,'original_title':original,'alternate_titles':[],'category':category,'format':fmt,'original_language':('Japanese' if category.startswith('anime')and v['id']!='wRs4Y3Kzdt0' else 'Not confirmed' if author=='Shemaroo Movies' else audio),'audio_label':audio+' audio','country':country,'year':year,'genre':genre,'provider':author,'watch_url':url,'synopsis':synopsis,'color':'#a4cbb7','motif':'moss','word':'ANILOVE','availability':'embedded','india_playback':'unverified','region_note':'India appears in country metadata; actual India playback is unverified.','last_checked':'2026-10-16','verification_method':'Official uploader, full runtime and oEmbed metadata','metadata_sources':[url],'thumbnail':'https://i.ytimg.com/vi/'+v['id']+'/hqdefault.jpg','seasons':[season],'related':[]};data.append(t);byid[tid]=t
 (ROOT/'data/catalogue.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'titles':len(data),'categories':{c:sum(t['category']==c for t in data)for c in ['anime-series','anime-movies','movies','k-dramas']},'uploads':sum(len(s['episodes'])for t in data for s in t['seasons'])}))
