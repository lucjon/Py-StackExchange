import stackexchange, unittest

QUESTION_ID = 4
ANSWER_ID = 98

def _setUp(self):
	self.site = stackexchange.Site(stackexchange.StackOverflow)

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
		q = self.site.question(QUESTION_ID, body=True)
		self.assertTrue(self.site.rate_limit is not None)

	def test_vectorise(self):
		q = self.site.question(QUESTION_ID)
		v = self.site.vectorise((q, 100, '200'), or_of_type=stackexchange.Question)
		self.assertEqual(v, '4;100;200')

if __name__ == '__main__':
	unittest.main()
