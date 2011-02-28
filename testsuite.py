import stackexchange, unittest

QUESTION_ID = 4
ANSWER_ID = 98

class DataTests(unittest.TestCase):
	def setUp(self):
		self.site = stackexchange.Site(stackexchange.StackOverflow)
	
	def test_fetch_question(self):
		s = self.site.question(QUESTION_ID)
		self.assertEqual(s.title, u"When setting a form's opacity should I use a decimal or double?")
	
	def test_fetch_answer(self):
		s = self.site.answer(ANSWER_ID)
	
	def test_has_body(self):
		q = self.site.question(QUESTION_ID, body=True)
		self.assertTrue(hasattr(q, 'body'))
		self.assertNotEqual(q.body, None)

		a = self.site.answer(ANSWER_ID, body=True)
		self.assertTrue(hasattr(q, 'body'))
		self.assertNotEqual(q.body, None)

class PlumbingTests(unittest.TestCase):
	#def test_key_ratelimit(self):
	pass

if __name__ == '__main__':
	unittest.main()
