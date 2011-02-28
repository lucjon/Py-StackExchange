import stackexchange, unittest, stacksites

QUESTION_ID = 4
ANSWER_ID = 98

def _setUp(self):
	self.site = stackexchange.Site(stackexchange.StackOverflow, '1_9Gj-egW0q_k1JaweDG8Q')

class DataTests(unittest.TestCase):
	def setUp(self):
		_setUp(self)
	
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
	def setUp(self):
		_setUp(self)
	
	def test_key_ratelimit(self):
		# a key was given, so check the rate limit is 10000
		if not hasattr(self.site, 'rate_limit'):
			self.site.question(QUESTION_ID)
		self.assertTrue(self.site.rate_limit[1] == 10000)
	
	def test_site_constants(self):
		# SOFU should always be present
		self.assertTrue(hasattr(stacksites, 'StackOverflow'))
		self.assertTrue(hasattr(stacksites, 'ServerFault'))
		self.assertTrue(hasattr(stacksites, 'SuperUser'))
	
	def test_vectorise(self):
		# check different types
		q = self.site.question(QUESTION_ID)
		v = self.site.vectorise(('hello', 10, True, False, q), stackexchange.Question)
		self.assertEqual(v, 'hello;10;true;false;%d' % QUESTION_ID)

if __name__ == '__main__':
	unittest.main()
