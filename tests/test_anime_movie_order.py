import json,re,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class AnimeMovieOrdering(unittest.TestCase):
 def test_movie_rail_static_category_and_live_search_share_owner_order(self):
  catalogue=json.loads((ROOT/'data/catalogue.json').read_text())
  expected=[t['id']for t in sorted((t for t in catalogue if t['category']=='anime-movies'),key=lambda t:t.get('browse_priority',100))]
  category=(ROOT/'dist/category/anime-movies/index.html').read_text()
  self.assertEqual(re.findall(r'<article class="title-card" data-id="([^"]+)"',category),expected)
  home=(ROOT/'dist/index.html').read_text();rail=home.split('Anime movie night',1)[1].split('<section class="editorial-banner"',1)[0]
  self.assertEqual(re.findall(r'<article class="title-card" data-id="([^"]+)"',rail),expected)
  # Execute the actual search renderer with a minimal DOM to catch client/server order divergence.
  function=next(line for line in (ROOT/'assets/app.js').read_text().splitlines()if line.startswith('function filter()'))
  code='''const catalogue=JSON.parse(require('fs').readFileSync(0,'utf8'));const elements={"#query":{value:""},".catalogue":{dataset:{category:"anime-movies"}},"#results":{},"#result-count":{},"#empty":{}};const $=key=>elements[key]||null;const localCard=t=>t.id+"|";const history={replaceState(){}};const location={pathname:"/category/anime-movies/"};'''+function+';filter();console.log(elements["#results"].innerHTML);'
  rendered=subprocess.check_output(['node','-e',code],input=json.dumps(catalogue,ensure_ascii=False),text=True)
  self.assertEqual(rendered.strip().removeprefix('<div class="cards">').removesuffix('</div>').strip('|').split('|'),expected)

if __name__=='__main__':unittest.main()
