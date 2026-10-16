import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class IndiaCatalogue(unittest.TestCase):
 def test_chart_request_blocks_are_removed(self):
  self.assertFalse((ROOT/'dist/india-trending').exists())
  self.assertFalse((ROOT/'dist/trending-sources').exists())
  for path in ['index.html','category/movies/index.html','category/k-dramas/index.html']:
   page=(ROOT/'dist'/path).read_text();self.assertNotIn('trend-card',page);self.assertNotIn('Full YouTube upload not verified',page);self.assertNotIn('Request this title',page)
 def test_season_controls_resolve_to_actual_panels(self):
  for title in json.loads((ROOT/'data/catalogue.json').read_text()):
   page=(ROOT/'dist/title'/title['id']/'index.html').read_text()
   targets=re.findall(r'data-season-target="([^"]+)"',page)
   panels=re.findall(r'data-season-panel id="([^"]+)"',page)
   self.assertEqual(targets,panels,title['id']);self.assertEqual(len(targets),len(title['seasons']))
 def test_new_movies_have_checked_full_uploads_and_english_captions(self):
  checks={v['id']:v for v in json.loads((ROOT/'data/expansion-verification.json').read_text())}
  films=[t for t in json.loads((ROOT/'data/catalogue.json').read_text())if t['provider']=='GUNDAM CHANNEL INTL']
  self.assertEqual(len(films),4)
  for film in films:
   self.assertEqual(film['category'],'anime-movies')
   for season in film['seasons']:
    self.assertIn('English',season['subtitle_languages'])
    for episode in season['episodes']:
     checked=checks[episode['video_id']];self.assertTrue(checked['eligible']);self.assertTrue(checked['india_in_country_metadata']);self.assertIn('en',checked['caption_languages']);self.assertGreater(checked['seconds'],3600)
if __name__=='__main__':unittest.main()
