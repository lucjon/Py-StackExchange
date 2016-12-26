import datetime, time

from six.moves import urllib
from six import string_types

from stackexchange.web import WebRequestManager
from stackexchange.core import *
from stackexchange.models import *

##### Site metadata ###
# (originally in the stackauth module; now we need it for Site#info)

class SiteState(Enumeration):
    """Describes the state of a StackExchange site."""
    Normal, OpenBeta, ClosedBeta, LinkedMeta = range(4)

class SiteType(Enumeration):
    '''Describes the type (meta or non-meta) of a StackExchange site.'''
    MainSite, MetaSite = range(2)

class MarkdownExtensions(Enumeration):
    '''Specifies one of the possible extensions to Markdown a site can have enabled.'''
    MathJax, Prettify, Balsamiq, JTab = range(4)

class SiteDefinition(JSONModel):
    """Contains information about a StackExchange site, reported by StackAuth."""
    transfer = ('aliases', 'api_site_parameter', 'audience', 'favicon_url',
        'high_resolution_icon_url', 'icon_url', 'logo_url', 'name', 'open_beta_date',
        'related_sites', 'site_state', 'site_type', 'site_url', 'twitter_account',
        'api_site_parameter',
        ('closed_beta_date', UNIXTimestamp),
        ('open_beta_date', UNIXTimestamp),
        ('launch_date', UNIXTimestamp),
        ('markdown_extensions', ListOf(MarkdownExtensions.from_string)),
        ('site_state', SiteState.from_string),
        ('site_type', SiteType.from_string),
        ('styling', DictObject))

    # To maintain API compatibility only; strictly speaking, we should use api_site_parameter
    # to create new sites, and that's what we do in get_site()
    alias = (('api_endpoint', 'site_url'), ('description', 'audience'))


    def _extend(self, json, stackauth):
        # The usual enumeration heuristics need a bit of help to parse the
        # site state as returned by the API
        fixed_state = re.sub(r'_([a-z])', lambda match: match.group(1).upper(), json.site_state)
        fixed_state = fixed_state[0].upper() + fixed_state[1:]
        self.state = SiteState.from_string(fixed_state)
    
    def get_site(self, *a, **kw):
        return Site(self.api_site_parameter, *a, **kw)

##### Statistics    ###
class Statistics(JSONModel):
    """Stores statistics for a StackExchange site."""
    transfer = ('new_active_users', 'total_users', 'badges_per_minute',
        'total_badges', 'total_votes', 'total_comments', 'answers_per_minute',
        'questions_per_minute', 'total_answers', 'total_accepted',
        'total_unanswered', 'total_questions', 'api_revision')
    alias = (('site_definition', 'site', ModelRef(SiteDefinition)),)


class Site(object):
    """Stores information and provides methods to access data on a StackExchange site. This class is the 'root' of the API - all data is accessed
through here."""

    def __init__(self, domain, app_key = None, cache = 1800, impose_throttling = False, force_http = False):
        self.domain = domain
        self.app_key = app_key
        self.api_version = '2.2'

        self.impose_throttling = impose_throttling
        self.throttle_stop = True
        self.cache_options = {'cache': False} if cache == 0 else {'cache': True, 'cache_age': cache}
        self.force_http = force_http

        self.include_body = False
        self.include_comments = False

        # In API v2.x, we generally don't get given api. at the start of these things, nor are they
        # strictly domains in many cases. We continue to accept api.* names for compatibility.
        domain_components = self.domain.split('.')
        if domain_components[0] == 'api':
            self.root_domain = '.'.join(domain_components[1:])
        else:
            self.root_domain = domain

    URL_Roots = {
        User: 'users/%s',
        Badge: 'badges/%s',
        Answer: 'answers/%s',
        Comment: 'comments/%s',
        Question: 'questions/%s',
    }

    def check_filter(self, kw):
        if 'answers' not in kw:
            kw['answers'] = 'true'
        if self.include_body:
            kw['body'] = 'true'
        if self.include_comments:
            kw['comments'] = 'true'

        # for API v2.x, the comments, body and answers parameters no longer
        # exist; instead, we have to use filters. for now, take the easy way
        # out and just rewrite them in terms of the new filters.
        if 'filter' not in kw:
            filter_name = '_'

            if kw.get('body'):
                filter_name += 'b'
                del kw['body']
            if kw.get('comments'):
                filter_name += 'c'
                del kw['comments']
            if kw.get('answers'):
                filter_name += 'a'
                del kw['answers']

            if filter_name == '_ca':
                # every other compatibility filter name works in the above
                # order except this one...
                kw['filter'] = '_ac'
            elif filter_name != '_':
                kw['filter'] = filter_name

    def _kw_to_str(self, ob):
        try:
            if isinstance(ob, datetime.datetime):
                return str(time.mktime(ob.timetuple()))
            elif isinstance(ob, string_types):
                return ob
            else:
                i = iter(ob)
                return ';'.join(i)
        except TypeError:
            return str(ob).lower()

    def _request(self, to, params):
        url = 'api.stackexchange.com/' + self.api_version + '/' + to
        params['site'] = params.get('site', self.root_domain)

        new_params = {}
        for k, v in params.items():
            if v is None:
                pass
            elif k in ('fromdate', 'todate'):
                # bit of a HACKish workaround for a reported issue; force to an integer
                new_params[k] = str(int(v))
            else:
                new_params[k] = self._kw_to_str(v)

        if self.app_key != None:
            new_params['key'] = self.app_key

        request_properties = dict([(x, getattr(self, x)) for x in ('impose_throttling', 'throttle_stop', 'force_http')])
        request_properties.update(self.cache_options)
        request_mgr = WebRequestManager(**request_properties)

        json, info = request_mgr.json_request(url, new_params)

        if 'quota_remaining' in json and 'quota_max' in json:
            self.rate_limit = (json['quota_remaining'], json['quota_max'])
            self.requests_used = self.rate_limit[1] - self.rate_limit[0]
            self.requests_left = self.rate_limit[0]

        return json

    def _user_prop(self, qs, typ, coll, kw, prop = 'user_id'):
        if prop not in kw:
            raise LookupError('No user ID provided.')
        else:
            tid = self.vectorise(kw[prop], User)
            del kw[prop]

            return self.build('users/%s/%s' % (tid, qs), typ, coll, kw)

    def be_inclusive(self):
        """Include the body and comments of a post, where appropriate, by default."""
        self.include_body, self.include_comments = True, True

    def build(self, url, typ, collection, kw = {}):
        """Builds a StackExchangeResultset object from the given URL and type."""
        if 'body' not in kw:
            kw['body'] = str(self.include_body).lower()
        if 'comments' not in kw:
            kw['comments'] = str(self.include_comments).lower()

        json = self._request(url, kw)
        return JSONMangler.json_to_resultset(self, json, typ, collection, (self, url, typ, collection, kw))

    def build_from_snippet(self, json, typ):
        return StackExchangeResultset([typ(x, self) for x in json])

    def vectorise(self, lst, or_of_type = None):
        # Ensure we're always dealing with an iterable
        allowed_types = or_of_type
        if allowed_types is not None and not hasattr(allowed_types, '__iter__'):
            allowed_types = (allowed_types, )

        if isinstance(lst, string_types) or type(lst).__name__ == 'bytes':
            return lst
        elif hasattr(lst, '__iter__'):
            return ';'.join([self.vectorise(x, or_of_type) for x in lst])
        elif allowed_types is not None and any([isinstance(lst, typ) for typ in allowed_types]) and hasattr(lst, 'id'):
            return str(lst.id)
        else:
            return str(lst).lower()

    def _get(self, typ, ids, coll, kw):
        root = self.URL_Roots[typ] % self.vectorise(ids)
        return self.build(root, typ, coll, kw)


    def user(self, nid, **kw):
        """Retrieves an object representing the user with the ID `nid`."""
        u, = self.users((nid,), **kw)
        return u

    def users(self, ids = [], **kw):
        """Retrieves a list of the users with the IDs specified in the `ids' parameter."""
        if 'filter' not in kw:
            # Include answer_count, etc. in the default filter
            kw['filter'] = '!-*f(6q3e0kcP'
        return self._get(User, ids, 'users', kw)
    
    def users_by_name(self, name, **kw):
        kw['filter'] = name
        return self.users(**kw)

    def moderators(self, **kw):
        """Retrieves a list of the moderators on the site."""
        return self.build('users/moderators', User, 'users', kw)

    def moderators_elected(self, **kw):
        """Retrieves a list of the elected moderators on the site."""
        return self.build('users/moderators/elected', User, 'users', kw)

    def answer(self, nid, **kw):
        """Retrieves an object describing the answer with the ID `nid`."""
        a, = self.answers((nid,), **kw)
        return a

    def answers(self, ids = None, **kw):
        """Retrieves a set of the answers with the IDs specified in the 'ids' parameter, or by the
        user_id specified."""
        self.check_filter(kw)
        if ids is None and 'user_id' in kw:
            return self._user_prop('answers', Answer, 'answers', kw)
        elif ids is None:
            return self.build('answers', Answer, 'answers', kw)
        else:
            return self._get(Answer, ids, 'answers', kw)

    def comment(self, nid, **kw):
        """Retrieves an object representing a comment with the ID `nid`."""
        c, = self.comments((nid,), **kw)
        return c

    def comments(self, ids = None, posts = None, **kw):
        """Returns all the comments on the site."""
        if ids is None:
            if posts is None:
                return self.build('comments', Comment, 'comments', kw)
            else:
                url = 'posts/%s/comments' % self.vectorise(posts, (Question, Answer))
                return self.build(url, Comment, 'comments', kw)
        else:
            return self.build('comments/%s' % self.vectorise(ids), Comment, 'comments', kw)

    def question(self, nid, **kw):
        """Retrieves an object representing a question with the ID `nid`. Note that an answer ID can not be specified -
unlike on the actual site, you will receive an error rather than a redirect to the actual question."""
        q, = self.questions((nid,), **kw)
        return q

    questions = property(lambda s: QuestionsQuery(s))

    def recent_questions(self, **kw):
        """Returns the set of the most recent questions on the site, by last activity."""
        if 'answers' not in kw:
            kw['answers'] = 'true'
        return self.build('questions', Question, 'questions', kw)

    def badge_recipients(self, bids, **kw):
        """Returns a set of badges recently awarded on the site, constrained to those with the given IDs, with the 'user' property set describing the user to whom it was awarded."""
        return self.build('badges/%s/recipients' % self.vectorise(bids), Badge, 'badges', kw)

    def all_badges(self, **kw):
        """Returns the set of all the badges which can be awarded on the site, excluding those which are awarded for specific tags."""
        return self.build('badges', Badge, 'badges', kw)

    def badges(self, ids = None, **kw):
        """Returns the badge objectss with the given IDs."""
        if ids == None:
            return self._user_prop('badges', Badge, 'users', kw)
        else:
            return self._get(Badge, ids, 'users', kw)

    def badge(self, nid = None, name = None, **kw):
        """Returns an object representing the badge with the ID 'nid', or with the name passed in as name=."""
        if nid is not None and name is None:
            b, = self.build('badges/%d' % nid, Badge, 'badges', kw)
            return b
        elif nid is None and name is not None:
            # We seem to need to get all badges and find it by name. Sigh.
            kw['inname'] = name
            all_badges = self.build('badges', Badge, 'badges', kw)
            for badge in all_badges:
                if badge.name == name:
                    return badge
            return None
        else:
            raise KeyError('Supply exactly one of the following: a badge ID, a badge name')

    def privileges(self, **kw):
        """Returns all the privileges a user can have on the site."""
        return self.build('privileges', Privilege, 'privileges', kw)

    def all_nontag_badges(self, **kw):
        """Returns the set of all badges which are not tag-based."""
        return self.build('badges/name', Badge, 'badges', kw)

    def all_tag_badges(self, **kw):
        """Returns the set of all the tag-based badges: those which are awarded for performance on a specific tag."""
        return self.build('badges/tags', Badge, 'badges', kw)

    def all_tags(self, **kw):
        '''Returns the set of all tags on the site.'''
        return self.build('tags', Tag, 'tags', kw)

    def info(self, **kw):
        '''Returns statistical information and metadata about the site, such as the total number of questions.
        
Call with site=True to receive a SiteDefinition object representing this site in the site_definition field of the result.'''
        if kw.get('site'):
            # we need to remove site as a query parameter anyway to stop API
            # getting confused
            del kw['site']
            if 'filter' not in kw:
                kw['filter'] = '!9YdnSFfpS'

        return self.build('info', Statistics, 'statistics', kw)[0]

    def stats(self, *a, **kw):
        '''An alias for Site.info().'''
        # this is just an alias to info(), since the method name has changed since
        return self.info(*a, **kw)

    def revision(self, post, guid, **kw):
        real_id = post.id if isinstance(post, Question) or isinstance(post, Answer) else post
        return self.build('revisions/%d/%s' % (real_id, guid), PostRevision, 'revisions', kw)[0]

    def revisions(self, post, **kw):
        return self.build('revisions/' + self.vectorise(post, (Question, Answer)), PostRevision, 'revisions', kw)

    def search(self, **kw):
        return self.build('search', Question, 'questions', kw)

    def search_advanced(self, **kw):
        kw['body'] = None
        kw['comments'] = None
        return self.build('search/advanced', Question, 'questions', kw)

    def similar(self, title, tagged = None, nottagged = None, **kw):
        if 'answers' not in kw:
            kw['answers'] = True
        if tagged is not None:
            kw['tagged'] = self.vectorise(tagged, Tag)
        if nottagged is not None:
            kw['nottagged'] = self.vectorise(nottagged, Tag)

        kw['title'] = title
        return self.build('similar', Question, 'questions', kw)

    def tags(self, **kw):
        return self.build('tags', Tag, 'tags', kw)

    def tag(self, tag, **kw):
        return self.build('tags/%s/info' % tag, Tag, 'tags', kw)[0]

    def tag_wiki(self, tag, **kw):
        return self.build('tags/%s/wikis' % tag, TagWiki, 'tags', kw)

    def tag_related(self, tag, **kw):
        return self.build('tags/%s/related' % tag, Tag, 'tags', kw)

    def tag_synonyms(self, **kw):
        return self.build('tags/synonyms', TagSynonym, 'tag_synonyms', kw)

    def error(self, id, **kw):
        # for some reason, the SE API couldn't possible just ignore site=
        kw['site'] = None
        return self._request('errors/%d' % id, kw)

    def __add__(self, other):
        if isinstance(other, Site):
            return CompositeSite(self, other)
        else:
            raise NotImplemented

class CompositeSite(object):
    def __init__(self, s1, s2):
        self.site_one = s1
        self.site_two = s2

    def __getattr__(self, a):
        if hasattr(self.site_one, a) and hasattr(self.site_two, a) and callable(getattr(self.site_one, a)):
            def handle(*ps, **kws):
                res1 = getattr(self.site_one, a)(*ps, **kws)
                res2 = getattr(self.site_two, a)(*ps, **kws)

                if hasattr(res1, '__iter__') and hasattr(res2, '__iter__'):
                    return res1 + res2
                else:
                    return (res1, res2)

            return handle
        else:
            raise AttributeError(a)

    def __sub__(self, other):
        if other is self.site_one:
            return self.site_two
        elif other is self.site_two:
            return self.site_one
        else:
            raise NotImplemented
