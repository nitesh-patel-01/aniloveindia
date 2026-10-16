import importlib.util,json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('episode_import',ROOT/'scripts/expand_episode_lists.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class EpisodeNavigation(unittest.TestCase):
 def test_absolute_number_uses_season_relative_number(self):self.assertEqual(module.key('SPY×FAMILY - Episode 30 (S2E05) [Hindi dub]'),(2,'5'))
 def test_split_episode_keeps_part(self):self.assertEqual(module.key('Re:ZERO Director’s Cut | Episode 01B (EP02)'),(1,'1b'))
 def test_combined_upload_is_not_four_invented_uploads(self):self.assertEqual(module.key('Classroom of the Elite 4th Season - Episode 01～04 [English Sub]'),(4,'1-4'))
 def test_trailer_does_not_become_episode(self):self.assertIsNone(module.key('Classroom of the Elite - PV1'))
 def test_episode_page_uses_exact_selected_upload(self):
  for t in json.loads((ROOT/'data/catalogue.json').read_text()):
   for s in t['seasons']:
    for e in s['episodes']:
     page=ROOT/'dist/watch'/s['id']/str(e['number'])/'index.html'
     self.assertTrue(page.exists(),str(page))
     text=page.read_text();self.assertIn('data-video="'+e['video_id']+'"',text)
     self.assertEqual(text.count('aria-current="page"'),1)
     self.assertNotIn('data-playlist=',text)
if __name__=='__main__':unittest.main()
