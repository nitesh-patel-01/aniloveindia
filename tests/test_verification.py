import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from daily import eligible,validate_candidate
class Gates(unittest.TestCase):
 def video(self):return {'snippet':{'channelId':'official'},'status':{'privacyStatus':'public','embeddable':True},'contentDetails':{'duration':'PT24M','regionRestriction':{'allowed':['IN']}}}
 def test_eligible(self):self.assertTrue(eligible(self.video(),'official'))
 def test_private(self):
  v=self.video();v['status']['privacyStatus']='private';self.assertFalse(eligible(v,'official'))
 def test_no_embed(self):
  v=self.video();v['status']['embeddable']=False;self.assertFalse(eligible(v,'official'))
 def test_wrong_channel(self):self.assertFalse(eligible(self.video(),'unofficial'))
 def test_india_blocked(self):
  v=self.video();v['contentDetails']['regionRestriction']={'blocked':['IN']};self.assertFalse(eligible(v,'official'))
 def test_trailer_duration(self):
  v=self.video();v['contentDetails']['duration']='PT90S';self.assertFalse(eligible(v,'official'))
 def test_missing_episode(self):
  c={'channel_id':'official','expected_episode_numbers':[1,2],'episodes':[{'number':1,'video_id':'abc'}]};ok,errors=validate_candidate(c,None,{'official'});self.assertFalse(ok);self.assertIn('Episode order does not match expected list',errors)
 def test_no_api_does_not_pass(self):
  c={'channel_id':'official','authorization_evidence_url':'https://example.org','metadata_source_url':'https://example.org','audio_language':'Japanese','expected_episode_numbers':[1],'episodes':[{'number':1,'video_id':'abc'}]};self.assertFalse(validate_candidate(c,None,{'official'})[0])
if __name__=='__main__':unittest.main()
