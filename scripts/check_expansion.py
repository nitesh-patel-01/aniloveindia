import json,concurrent.futures
from pathlib import Path
from check_episode_uploads import check
ROOT=Path(__file__).resolve().parents[1]
q=json.loads((ROOT/'data/expansion-queue.json').read_text());p=ROOT/'data/expansion-verification.json';cached=json.loads(p.read_text())if p.exists()else [];out={x['id']:x for x in cached};todo=list(dict.fromkeys(v['video_id']for v in q if v.get('video_id')and v['video_id']not in out));print(json.dumps({'checking':len(todo)}),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=8)as pool:
 for i,r in enumerate(pool.map(check,todo)):
  out[r['id']]=r
  if (i+1)%10==0:p.write_text(json.dumps(list(out.values()),ensure_ascii=False,indent=2));print(json.dumps({'checked':len(out),'eligible':sum(x.get('eligible',False)for x in out.values())}),flush=True)
p.write_text(json.dumps(list(out.values()),ensure_ascii=False,indent=2));print(json.dumps({'total':len(out),'eligible':sum(x.get('eligible',False)for x in out.values())}),flush=True)
