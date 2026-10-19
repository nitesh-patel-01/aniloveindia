import json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Search(unittest.TestCase):
 def run_search(self, query, category=''):
  code=(ROOT/'assets/search.js').read_text().replace('export function','function')+"\nconst input=JSON.parse(require('fs').readFileSync(0,'utf8'));console.log(JSON.stringify(searchCatalogue(input.catalogue,input.query,input.category).map(t=>t.id)));"
  result=subprocess.check_output(['node','-e',code],input=json.dumps({'catalogue':json.loads((ROOT/'data/catalogue.json').read_text()),'query':query,'category':category}),text=True)
  return json.loads(result)
 def test_spacing_accents_and_punctuation(self):
  self.assertIn('dan-da-dan', self.run_search('dan da dan'))
  self.assertIn('pokemon-journeys',self.run_search('pokemon journeys'))
  self.assertIn('spy-x-family',self.run_search('spy family'))
  self.assertIn('hunter-x-hunter',self.run_search('hunter hunter'))
 def test_words_language_and_short_typo(self):
  self.assertIn('pokemon-journeys',self.run_search('watch journeys pokemon in Hindi'))
  self.assertIn('pokemon-journeys',self.run_search('pokmon journeys'))
 def test_scope_and_missing_requests(self):
  self.assertEqual(self.run_search('pokemon','movies'),[])
  self.assertEqual(self.run_search('totally missing zzzzz'),[])
 def test_new_module_copied(self):
  self.assertTrue((ROOT/'dist/assets/search.js').exists())
  index=json.loads((ROOT/'dist/data/search-index.json').read_text());full=json.loads((ROOT/'data/catalogue.json').read_text());self.assertEqual(len(index),len(full));self.assertEqual(sum(t['upload_count']for t in index),sum(len(s['episodes'])for t in full for s in t['seasons']));self.assertLess((ROOT/'dist/data/search-index.json').stat().st_size,(ROOT/'dist/data/catalogue.json').stat().st_size/3)
if __name__=='__main__':unittest.main()
