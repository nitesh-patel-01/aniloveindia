import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def slug(x):return re.sub(r'[^a-z0-9]+','-',x.lower()).strip('-')
class UploadDate(unittest.TestCase):
 def test_watch_pages_upload_date_has_timezone(self):
  # Search Console 2026-10-31: bare YYYY-MM-DD uploadDate flagged "invalid datetime" + "missing timezone".
  pat=re.compile(r'"uploadDate"\s*:\s*"([^"]+)"')
  checked=0
  for t in json.loads((ROOT/'data/catalogue.json').read_text()):
   for s in t['seasons']:
    if not s.get('embed_checked'):continue
    for e in s['episodes']:
     page=ROOT/'dist/watch'/slug(s['id'])/str(e['number'])/'index.html'
     m=pat.search(page.read_text())
     self.assertTrue(m,'uploadDate missing on '+str(page))
     self.assertRegex(m.group(1),r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([+-]\d{2}:\d{2}|Z)$',str(page))
     checked+=1
  self.assertGreater(checked,0)
if __name__=='__main__':unittest.main()
