import json,unittest,xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class JsonScripts(HTMLParser):
 def __init__(self):super().__init__();self.active=False;self.items=[]
 def handle_starttag(self,tag,attrs):
  if tag=='script'and dict(attrs).get('type')=='application/ld+json':self.active=True
 def handle_data(self,data):
  if self.active:self.items.append(json.loads(data))
 def handle_endtag(self,tag):
  if tag=='script':self.active=False
class LandingPages(unittest.TestCase):
 def test_live_collections_have_matching_schema_and_crawl_links(self):
  sitemap=(ROOT/'dist/sitemap.xml').read_text();ET.fromstring(sitemap)
  for slug in ['pokemon-hindi-episodes','hindi-anime-movies']:
   page=(ROOT/'dist/discover'/slug/'index.html').read_text();parser=JsonScripts();parser.feed(page);graph=next(s['@graph']for s in parser.items if '@graph'in s)
   collection=next(s for s in graph if s['@type']=='CollectionPage');faq=next(s for s in graph if s['@type']=='FAQPage')
   self.assertGreater(collection['mainEntity']['numberOfItems'],0);self.assertEqual(len(faq['mainEntity']),6);self.assertIn(collection['url'],sitemap);self.assertIn('<blockquote>',page);self.assertIn('index,follow',page)
   nav=page.split('<nav aria-label="Main navigation">')[1].split('</nav>')[0];self.assertNotIn(slug,nav)
if __name__=='__main__':unittest.main()
