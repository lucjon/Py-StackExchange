import logging

import datetime, re, stackauth, stackexchange, stackexchange.web, unittest
import stackexchange.sites as stacksites
from stackexchange.core import StackExchangeError
# for Python 3 compatiblity
try:
    import htmlentitydefs
except ImportError:
    import html.entities as htmlentitydefs

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
        self.assertEqual(html_unescape(s.title), u"While applying opacity to a form should we use a decimal or double value?")

    def test_fetch_answer(self):
        s = self.site.answer(ANSWER_ID)

    def test_fetch_answer_owner(self):
        s = self.site.answer(ANSWER_ID)
        self.assertIsInstance(s.owner_id, int)
        self.assertIsNotNone(s.owner)

    def test_fetch_answer_question(self):
        s = self.site.answer(ANSWER_ID)
        self.assertIsInstance(s.question_id, int)
        self.assertIsNotNone(s.question)

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
    
    def test_post_revisions(self):
        a = self.site.answer(4673436)
        a.revisions.fetch()
        first_revision = a.revisions[0]
        self.assertNotEqual(first_revision, None)
        self.assertEqual(first_revision.post_id, a.id)

    def test_has_body(self):
        q = self.site.question(QUESTION_ID, body=True)
        self.assertTrue(hasattr(q, 'body'))
        self.assertNotEqual(q.body, None)

        a = self.site.answer(ANSWER_ID, body=True)
        self.assertTrue(hasattr(a, 'body'))
        self.assertNotEqual(a.body, None)
    
    def test_tag_synonyms(self):
        syns = self.site.tag_synonyms()
        self.assertTrue(len(syns) > 0)
    
    def test_tag_wiki(self):
        tag = self.site.tag('javascript')
        self.assertEqual(tag.name, 'javascript')
        wiki = tag.wiki.fetch()
        self.assertTrue(len(wiki.excerpt) > 0)

    def test_tag_wiki2(self):
        wiki = self.site.tag_wiki('javascript')
        self.assertEqual(wiki[0].tag_name, 'javascript')
        wiki = self.site.tag_wiki('java;c++;python;android', page=1, pagesize=4)
        self.assertEqual(wiki[0].tag_name, 'android')
        self.assertEqual(wiki[1].tag_name, 'c++')
        self.assertEqual(wiki[2].tag_name, 'java')
        self.assertEqual(wiki[3].tag_name, 'python')

    def test_tag_related(self):
        related = self.site.tag_related('java', page=1, pagesize=40)
        names = tuple(tag.name for tag in related[:10])
        self.assertIn('android', names)
        self.assertIn('swing', names)

    def test_badge_name(self):
        badge = self.site.badge(name = 'Nice Answer')
        self.assertNotEqual(badge, None)
        self.assertEqual(badge.name, 'Nice Answer')
    
    def test_badge_id(self):
        badge = self.site.badge(23)
        self.assertEqual(badge.name, 'Nice Answer')
    
    def test_rep_change(self):
        user = self.site.user(41981)
        user.reputation_detail.fetch()
        recent_change = user.reputation_detail[0]
        self.assertNotEqual(recent_change, None)
        self.assertEqual(recent_change.user_id, user.id)

    def test_timeline(self):
        user = self.site.user(41981)
        user.timeline.fetch()
        event = user.timeline[0]
        self.assertNotEqual(event, None)
        self.assertEqual(event.user_id, user.id)
    
    def test_top_tag(self):
        user = self.site.user(41981)

        user.top_answer_tags.fetch()
        answer_tag = user.top_answer_tags[0]
        self.assertNotEqual(answer_tag, None)
        self.assertTrue(answer_tag.answer_count > 0)

        user.top_question_tags.fetch()
        question_tag = user.top_question_tags[0]
        self.assertNotEqual(question_tag, None)
        self.assertTrue(question_tag.question_count > 0)
    
    def test_privilege(self):
        privileges = self.site.privileges()
        self.assertTrue(len(privileges) > 0)
        self.assertTrue(privileges[0].reputation > 0)

    def test_stackauth_site_types(self):
        s = stackauth.StackAuth()
        for site in s.sites():
            self.assertTrue(site.site_type in (stackauth.SiteType.MainSite, stackauth.SiteType.MetaSite))
    
    def test_stackauth_site_instantiate(self):
        for defn in stackauth.StackAuth().sites():
            site_ob = defn.get_site(API_KEY)
            # Do the same as test_fetch_answer() and hope we don't get an exception
            defn.get_site(API_KEY).answer(ANSWER_ID)
            # Only do it once!
            break
    
    def test_advanced_search(self):
        results = self.site.search_advanced(q = 'python')
        self.assertTrue(len(results) > 0)

    def test_stats(self):
        results = self.site.stats()
        self.assertTrue(results.total_users > 0)

    def test_info_site_defn(self):
        result = self.site.info(site = True)
        self.assertNotEqual(result.site_definition, None)
        self.assertTrue(len(result.site_definition.name) > 0)
    
    def test_badge_recipients(self):
        results = self.site.badge_recipients(22)
        self.assertTrue(len(results) > 0)
        self.assertTrue(hasattr(results[0], 'user'))
        self.assertTrue(hasattr(results[0].user, 'id'))

    def test_badge_recipients_field(self):
        results = self.site.badge(22).recipients
        self.assertNotEqual(next(results), None)

    def test_accepted_answer(self):
        # our favourite test question...
        question = self.site.question(4)
        self.assertEqual(type(question.accepted_answer), stackexchange.Answer)
        self.assertEqual(question.accepted_answer.id, question.accepted_answer_id)

        ans = question.accepted_answer
        ans.fetch()
        self.assertTrue(hasattr(ans, 'score'))

    def test_moderators_elected(self):
        moderators = self.site.moderators_elected()
        self.assertGreater(len(moderators), 0)
        self.assertEqual(type(moderators[0]), stackexchange.User)


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
    
    def test_error(self):
        try:
            self.site.error(401)
        except Exception as e:
            self.assertEqual(type(e), StackExchangeError)
            self.assertEqual(e.code, 401)
        else:
            self.fail('did not raise exception on error')

    def test_vectorise(self):
        # check different types
        q = self.site.question(QUESTION_ID)
        v = self.site.vectorise(('hello', 10, True, False, q), stackexchange.Question)
        self.assertEqual(v, 'hello;10;true;false;%d' % QUESTION_ID)

    def test_total(self):
        r = self.site.search(tagged = 'python', filter = 'total')
        self.assertTrue(hasattr(r, 'total'))
        self.assertTrue(r.total > 0)

    def test_pagesize_independence(self):
        # this test is motivated by pull request #37

        # a slightly odd choice of tag indeed, but it has a modest but useful
        # number of questions and is unlikely to grow very quickly
        qs = self.site.questions(tagged = 'dijkstra', pagesize = 37, filter = '!9YdnSQVoS')
        total1 = qs.total
        count1 = len(list(qs))
        self.assertEqual(count1, total1)

        qs = self.site.questions(tagged = 'dijkstra', pagesize = 100, filter = '!9YdnSQVoS')
        total2 = qs.total
        count2 = len(list(qs))
        self.assertEqual(count2, total2)
        self.assertEqual(count1, count2)

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

    def test_partial(self):
        qn = self.site.question(4)
        comment = qn.comments.fetch()[0]
        owner = comment.owner.fetch()

if __name__ == '__main__':
    unittest.main()
