import json,subprocess,unittest
from pathlib import Path
from urllib.parse import urlparse,parse_qs
ROOT=Path(__file__).resolve().parents[1]
class RequestsAndSearchPages(unittest.TestCase):
 def test_whatsapp_destination_and_message_encoding(self):
  code="const fs=require('fs');const src=fs.readFileSync('assets/request.js','utf8');import('data:text/javascript,'+encodeURIComponent(src)).then(m=>console.log(m.whatsappRequestUrl('Anime & K-drama?','हिन्दी dub + English subtitles','https://example.test/search/')));"
  url=subprocess.check_output(['node','-e',code],cwd=ROOT,text=True).strip();p=urlparse(url)
  self.assertEqual(p.netloc,'wa.me');self.assertEqual(p.path,'/917974823298');message=parse_qs(p.query)['text'][0];self.assertIn('Anime & K-drama?',message);self.assertIn('हिन्दी dub + English subtitles',message);self.assertIn('\n\nPage: https://example.test/search/',message)
 def test_request_forms_use_whatsapp(self):
  for path in ['contact/index.html','search/index.html','category/movies/index.html']:
   html=(ROOT/'dist'/path).read_text();self.assertIn('Request on WhatsApp',html);self.assertNotIn('Prepare email',html)
 def test_search_pages_are_indexable_but_not_main_navigation(self):
  import sys
  sys.path.insert(0,str(ROOT));from seo_pages import PAGES
  home=(ROOT/'dist/index.html').read_text();sitemap=(ROOT/'dist/sitemap.xml').read_text()
  for item in PAGES:
   route='/discover/'+item['slug']+'/'
   self.assertNotIn(route,home);self.assertIn(route,sitemap)
   html=(ROOT/'dist'/route.lstrip('/')/'index.html').read_text();self.assertIn('index,follow',html);self.assertIn('FAQPage',html);self.assertIn('CollectionPage',html);self.assertIn('/title/',html)
 def test_new_uploads_have_full_length_checked_sources(self):
  data=json.loads((ROOT/'data/catalogue.json').read_text());checks={v['id']:v for v in json.loads((ROOT/'data/expansion-verification.json').read_text())};new=[t for t in data if t.get('added_on')=='2026-10-16'];self.assertEqual(len(new),16)
  for t in new:
   for s in t['seasons']:
    for ep in s['episodes']:
     self.assertTrue(checks[ep['video_id']]['eligible']);self.assertGreater(ep['duration_seconds'],3600 if t['format']=='Movie'else 1500)
if __name__=='__main__':unittest.main()
