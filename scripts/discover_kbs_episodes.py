import sys,json,re,urllib.request,urllib.parse,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from extract_discovery import walk
terms=['Gunman in Joseon','Who Are You School 2015','Hi School Love On','Master of Study','Hwangjini']
def scan(term):
 u='https://www.youtube.com/@kbsworldtv/search?query='+urllib.parse.quote(term)
 try:
  s=urllib.request.urlopen(u,timeout=35).read().decode();d=json.loads(re.search(r'var ytInitialData = (\{.*?\});',s)[1]);r=[]
  for v in walk(d,'videoRenderer'):
   title=''.join(x.get('text','')for x in v.get('title',{}).get('runs',[]));runtime=v.get('lengthText',{}).get('simpleText','');parts=runtime.split(':');seconds=sum(int(n)*60**i for i,n in enumerate(reversed(parts)))if all(n.isdigit()for n in parts)else 0
   if seconds>1500 and re.search(r'\bEp\.?\s*\d+',title,re.I)and not re.search(r'Part\.?\s*\d+',title,re.I):r.append({'video_id':v['videoId'],'title':title,'kind':'k-drama'})
  return r
 except Exception as e:print(term,str(e));return []
r=sum(list(concurrent.futures.ThreadPoolExecutor(max_workers=5).map(scan,terms)),[]);p=ROOT/'data/expansion-queue.json';q=json.load(open(p));q+=r;json.dump(q,open(p,'w'),ensure_ascii=False,indent=2);print('Added KBS candidates',len(r))
