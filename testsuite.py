import logging

import stackauth, stackexchange, stackexchange.web, unittest
import stackexchange.sites as stacksites
import htmlentitydefs, re

QUESTION_ID = 4
ANSWER_ID = 98
USER_ID = 23901
API_KEY = 'pXlviKYs*UZIwKLPwJGgpg(('

_l = logging.getLogger(__name__)

def _setUp(self):
	self.site = stackexchange.Site(stackexchange.StackOverflow, API_KEY, impose_throttling = True)

stackexchange.web.WebRequestManager.debug = True

htmlentitydefs.name2codepoint['#39'] = 39
def html_unescape(text):
    return re.sub('&(%s);' % '|'.join(htmlentitydefs.name2codepoint),
              lambda m: unichr(htmlentitydefs.name2codepoint[m.group(1)]), text)

class DataTests(unittest.TestCase):
	def setUp(self):
		_setUp(self)

	def test_fetch_paged(self):
		user = stackexchange.Site(stackexchange.Programmers, API_KEY).user(USER_ID)

		answers = user.answers.fetch(pagesize=60)
		for answer in answers:
			# dummy assert.. we're really testing paging here to make sure it doesn't get
			# stuck in an infinite loop. there very well may be a better way of testing this,
			# but it's been a long day and this does the trick
			# this used to test for title's presence, but title has been removed from the
			# default filter
			self.assertTrue(answer.id is not None)

	def test_fetch_question(self):
		s = self.site.question(QUESTION_ID)
		self.assertEqual(html_unescape(s.title), u"When setting a form's opacity should I use a decimal or double?")

	def test_fetch_answer(self):
		s = self.site.answer(ANSWER_ID)

	def test_fetch_answer_comment(self):
		# First try the comments on an answer with lots of comments
		# http://stackoverflow.com/a/22389702
		s = self.site.answer(22389702)
		s.comments.fetch()
		first_comment = s.comments[0]
		self.assertNotEqual(first_comment, None)
		self.assertTrue(first_comment.body)

	def test_fetch_question_comment(self):
		# Now try a question
		# http://stackoverflow.com/a/22342854
		s = self.site.question(22342854)
		s.comments.fetch()
		first_comment = s.comments[0]
		self.assertNotEqual(first_comment, None)
		self.assertTrue(first_comment.body)
	
	def test_question_revisions(self):
		q = self.site.question(4673436)
		q.revisions.fetch()
		first_revision = q.revisions[0]
		self.assertNotEqual(first_revision, None)
		self.assertEqual(first_revision.post_id, q.id)

	def test_has_body(self):
		q = self.site.question(QUESTION_ID, body=True)
		self.assertTrue(hasattr(q, 'body'))
		self.assertNotEqual(q.body, None)

		a = self.site.answer(ANSWER_ID, body=True)
		self.assertTrue(hasattr(q, 'body'))
		self.assertNotEqual(q.body, None)

	def test_stackauth_site_types(self):
		s = stackauth.StackAuth()
		for site in s.sites():
			self.assertTrue(site.site_type in {stackauth.SiteType.MainSite, stackauth.SiteType.MetaSite})
	
	def test_stackauth_site_instantiate(self):
		for defn in stackauth.StackAuth().sites():
			site_ob = defn.get_site()
			# Do the same as test_fetch_answer() and hope we don't get an exception
			defn.get_site().answer(ANSWER_ID)
			# Only do it once!
			break


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

	def test_resultset_independence(self):
		# repro code for bug #4 (thanks, beaumartinez!)

		# Create two different sites.
		a = stackexchange.Site('api.askubuntu.com')
		b = self.site

		# Create two different searches from the different sites.
		a_search = a.search(intitle='vim', pagesize=100)
		b_search = b.search(intitle='vim', pagesize=100)

		# (We demonstrate that the second search has a second page.)
		self.assertEqual(len(b_search.fetch_next()), 100)

		# Reset the searches.
		a_search = a.search(intitle='vim', pagesize=100)
		b_search = b.search(intitle='vim', pagesize=100)

		# Exhaust the first search.
		while len(a_search) > 0:
			    a_search = a_search.fetch_next()

		# Try get the next page of the second search. It will be empty.
		# Here's the bug.
		self.assertEqual(len(b_search.fetch_next()), 100)


if __name__ == '__main__':
	unittest.main()
