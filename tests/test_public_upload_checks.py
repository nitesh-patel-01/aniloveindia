"""Exercise public metadata gates without downloading media or contacting YouTube."""
import json,sys,unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_episode_uploads import check
CHANNEL='UCejtUitnpnf8Be-v5NuDSLw'
class Response:
 def __init__(self,text):self.text=text
 def read(self):return self.text.encode()
class PublicUploadChecks(unittest.TestCase):
 def player(self):return {'videoDetails':{'channelId':CHANNEL,'author':'GUNDAM CHANNEL INTL','title':'Episode 1','lengthSeconds':'1462'},'microformat':{'playerMicroformatRenderer':{'embed':{'iframeUrl':'https://www.youtube.com/embed/abcdefghijk'},'availableCountries':['IN'],'publishDate':'2026-10-08'}},'playabilityStatus':{'status':'OK'}}
 def run_check(self,player):
  def fetch(url,**kwargs):
   if '/oembed?' in url:return Response(json.dumps({'html':'<iframe></iframe>','author_name':'GUNDAM CHANNEL INTL'}))
   return Response('var ytInitialPlayerResponse = '+json.dumps(player)+';')
  with patch('urllib.request.urlopen',side_effect=fetch):return check('abcdefghijk')
 def test_current_date_and_valid_public_upload(self):
  r=self.run_check(self.player());self.assertTrue(r['eligible']);self.assertEqual(r['checked_at'],datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat());self.assertEqual(r['actual_india_playback'],'unverified')
 def test_membership_rejected(self):
  p=self.player();p['playabilityStatus']={'status':'UNPLAYABLE','reason':'Join this channel to watch members-only content'};self.assertFalse(self.run_check(p)['eligible'])
 def test_future_premiere_rejected(self):
  p=self.player();p['videoDetails']['isUpcoming']=True;p['playabilityStatus']={'status':'LIVE_STREAM_OFFLINE','reason':'Premieres in 2 hours'};self.assertFalse(self.run_check(p)['eligible'])
 def test_unlisted_rejected(self):
  p=self.player();p['microformat']['playerMicroformatRenderer']['isUnlisted']=True;self.assertFalse(self.run_check(p)['eligible'])
 def test_unknown_unplayable_reason_rejected(self):
  p=self.player();p['playabilityStatus']={'status':'UNPLAYABLE','reason':'This video is unavailable'};self.assertFalse(self.run_check(p)['eligible'])
 def test_region_reason_does_not_certify_actual_india_playback(self):
  p=self.player();p['playabilityStatus']={'status':'UNPLAYABLE','reason':'Not available in your country'};r=self.run_check(p);self.assertTrue(r['eligible']);self.assertEqual(r['actual_india_playback'],'unverified')
 def test_india_absent_rejected(self):
  p=self.player();p['microformat']['playerMicroformatRenderer']['availableCountries']=['US'];self.assertFalse(self.run_check(p)['eligible'])
