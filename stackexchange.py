import urllib2, httplib, datetime, operator, StringIO, gzip
try:
	import json
except ImportError:
	import simplejson as json

# Site constants
StackOverflow = 'api.stackoverflow.com'
SuperUser = 'api.superuser.com'
ServerFault = 'api.serverfault.com'
StackApps = 'api.stackapps.com'
MetaStackOverflow = 'api.meta.stackoverflow.com'

#### Hack, because I can't be bothered to fix my mistaking JSON's output for an object not a dict
# Attrib: Eli Bendersky, http://stackoverflow.com/questions/1305532/convert-python-dict-to-object/1305663#1305663
class DictObject:
    def __init__(self, entries): 
        self.__dict__.update(entries)

class StackExchangeError(Exception):
	"""A generic error thrown on a bad HTTP request during a StackExchange API request."""
	def __init__(self, urlerror):
		self.urlerror = urlerror
	def __str__(self):
		return 'Received HTTP error \'%d\'.' % self.urlerror.code

class StackExchangeResultset(tuple):
	"""Defines an immutable, paginated resultset. This class can be used as a tuple, but provides extended metadata as well, including methods
to fetch the next page."""

	def __new__(cls, items, page, pagesize, build_info):
		cls.page, cls.pagesize, cls.build_info = page, pagesize, build_info
		return tuple.__new__(cls, items)
	
	def reload(self):
		"""Refreshes the data in the resultset with fresh API data. Note that this doesn't work with extended resultsets."""
		# kind of a cheat, but oh well
		return self.fetch_page(self.page)

	def fetch_page(self, page, **kw):
		"""Returns a new resultset containing data from the specified page of the results. It re-uses all parameters that were passed in
to the initial function which created the resultset."""
		new_params = list(self.build_info)
		new_params[4] = new_params[4].copy()
		new_params[4].update(kw)
		new_params[4]['page'] = page
		return new_params[0].build(*new_params[1:])
	
	def fetch_extended(self, page):
		"""Returns a new resultset containing data from this resultset AND from the specified page."""
		next = self.fetch_page(page)
		extended = self + next

		# max(0, ...) is so a non-zero, positive result for page is always found
		return StackExchangeResultset(extended, max(1, self.page - 1), self.pagesize + next.pagesize, self.build_info)

	def fetch_next(self):
		"""Returns the resultset of the data in the next page."""
		return self.fetch_page(self.page + 1)
	
	def extend_next(self):
		"""Returns a new resultset containing data from this resultset AND from the next page."""
		return self.fetch_extended(self.page + 1)

class Enumeration(object):
	"""Provides a base class for enumeration classes. (Similar to 'enum' types in other languages.)"""

	@classmethod
	def from_string(cls, text, typ=None):
		if typ is not None:
			if hasattr(typ, '_map') and text in typ._map:
				return getattr(typ, typ._map[text])
			elif hasattr(typ, text[0].upper() + text[1:]):
				return getattr(typ, text[0].upper() + text[1:])
			else:
				return None
		else:
			return cls.from_string(text, cls)

class NeedsAwokenError(Exception):
	"""An error raised when an attempt is made to access a property of a lazy collection that requires the data to have been fetched,
but whose data has not yet been requested."""

	def __init__(self, lazy):
		self.lazy = lazy
	def __str__(self):
		return 'Could not return requested data; the sequence of "%s" has not been fetched.' % self.lazy.m_lazy

class StackExchangeLazySequence(list):
	"""Provides a sequence which *can* contain extra data available on an object. It is 'lazy' in the sense that data is only fetched when
required - not on object creation."""

	def __init__(self, m_type, count, site, url, fetch=None, collection=None):
		self.m_type = m_type
		self.count = count
		self.site = site
		self.url = url
		self.fetch_callback = fetch
		self.collection = collection if collection != None else self._collection(url)
	
	def _collection(self, c):
		return c.split('/')[-1]

	def __len__(self):
		if self.count != None:
			return self.count
		else:
			raise NeedsAwokenError(self)
	
	def fetch(self, **kw):
		"""Fetch, from the API, the data this sequence is meant to hold."""

		res = self.site.build(self.url, self.m_type, self.collection, kw)
		if self.fetch_callback != None:
			self.fetch_callback(res)
		return res

## JSONModel base class
class JSONModel(object):
	"""The base class of all the objects which describe API objects directly - ie, those which take JSON objects as parameters to their constructor."""

	def __init__(self, json, site, skip_ext=False):
		self.json_ob = DictObject(json)
		self.site = site

		for f in [x for x in self.transfer if hasattr(self.json_ob, x)]:
			setattr(self, f, getattr(self.json_ob, f))

		if hasattr(self, '_extend') and not skip_ext:
			self._extend(self.json_ob, site)

	def fetch(self):
		"""Fetches all the data that the model can describe, not just the attributes which were specified in the original response."""
		if hasattr(self, 'fetch_callback'):
			res = self.fetch_callback(self, self.site)

			if isinstance(res, dict):
				self.__init__(res, self.site)
			elif hasattr(res, 'json_ob'):
				self.__init__(res.json_ob, self.site)
			else:
				raise ValueError('Supplied fetch callback did not return a usable value.')
		else:
			return False
	
	# Allows the easy creation of updateable, partial classes
	@classmethod
	def partial(cls, fetch_callback, site, populate):
		"""Creates a partial description of the API object, with the proviso that the full set of data can be fetched later."""

		model = cls({}, site, True)
		
		for k, v in populate.iteritems():
			setattr(model, k, v)

		model.fetch_callback = fetch_callback

	# for use with Lazy classes that need a callback to actually set the model property
	def _up(self, a):
		"""Returns a function which can be used with the LazySequence class to actually update the results properties on the model with the
new fetched data."""

		def inner(m):
			setattr(self, a, m)
		return inner

##### Statistics    ###
class Statistics(JSONModel):
	"""Stores statistics for a StackExchange site."""
	transfer = ('total_questions', 'total_unanswered', 'total_answers', 'total_comments', 'total_votes', 'total_badges', 'total_users', 'questions_per_minute', 'answers_per_minutes', 'badges_per_minute', 'display_name')

	def _extend(self, json, site):
		self.api_version = DictObject(json.api_version)

##### Content Types ###
class Answer(JSONModel):
	"""Describes an answer on a StackExchange site."""

	transfer = ('accepted', 'locked_date', 'question_id', 'up_vote_count', 'down_vote_count', 'view_count', 'score',
		'community_owned', 'title', 'body')

	def _extend(self, json, site):
		self.id = json.answer_id

		if not hasattr(json, '_params_'):
			comment = False
		else:
			comment = ('comment' in json._params_ and json._params_['comment'])
		self.comments = site.build_from_snippet(json.comments, Comment) if comment else StackExchangeLazySequence(Comment, None, site, json.answer_comments_url, self._up('comments'))

		self._question, self._owner = None, None
		if hasattr(json, 'owner'):
			self.owner_id = json.owner['user_id']
			self.owner_info = tuple(json.owner.values())

		self.creation_date = datetime.date.fromtimestamp(json.creation_date)

		if hasattr(json, 'last_edit_date'):
			self.last_edit_date = datetime.date.fromtimestamp(json.last_edit_date)
		if hasattr(json, 'last_activity_date'):
			self.last_activity_date = datetime.date.fromtimestamp(json.last_activity_date)

		self.votes = (self.up_vote_count, self.down_vote_count)
		self.url = 'http://' + self.site.root_domain + '/questions/' + str(self.question_id) + '/' + str(self.id) + '#' + str(self.id)
	
	def _get_user(s,id):
		s._owner = s.site.user(id)
		return s._owner
	def _set_user(s,ob):
		s._owner = pb
	def _get_quest(s,id):
		s._question = s.site.question(id)
		return s._question
	def _set_quest(s,ob):
		s._question = ob
	
	question = property(lambda self: self._question if self._question is not None else self._get_quest(self.question_id), _set_quest)
	owner = property(lambda self: self._owner if self._owner is not None else self._get_user(self.owner_id), _set_user)

	def __unicode__(self):
		return u'Answer %d [%s]' % (self.id, self.title)
	def __str__(self):
		return str(unicode(self))

class Question(JSONModel):
	"""Describes a question on a StackExchange site."""

	transfer = ('tags', 'favorite_count', 'up_vote_count', 'down_vote_count', 'view_count', 'score', 'community_owned', 'title', 'body')

	def _extend(self, json, site):
		self.id = json.question_id

		self.timeline = StackExchangeLazySequence(TimelineEvent, None, site, json.question_timeline_url, self._up('timeline'))

		self.comments_url = json.question_comments_url
		self.comments = StackExchangeLazySequence(Comment, None, site, self.comments_url, self._up('comments'))

		self.answers_url = json.question_answers_url
		if hasattr(json, 'answers'):
			self.answers = [Answer(x, site) for x in json.answers]

		if hasattr(json, 'owner'):
			self.owner_id = json.owner['user_id']
	
			owner_dict = json.owner
			owner_dict['id'] = self.owner_id
			del owner_dict['user_id']
			owner_dict['user_type'] = UserType.from_string(owner_dict['user_type'])
	
			self.owner = User.partial(lambda self: self.site.user(self.id), site, owner_dict)

		self.url = 'http://' + self.site.root_domain + '/questions/' + str(self.id)

class Comment(JSONModel):
	"""Describes a comment to a question or answer on a StackExchange site."""

	transfer = ('post_id', 'score', 'edit_count', 'body')
	def _extend(self, json, site):
		self.id = json.comment_id
		
		self.creation_date = datetime.date.fromtimestamp(json.creation_date)
		self.owner_id = json.owner['owner_id'] if 'owner_id' in json.owner else json.owner['user_id']
		self.owner = User.partial(lambda self: self.site.user(self.id), site, {
			'id': self.owner_id, 
			'user_type': Enumeration.from_string(json.owner['user_type'], UserType),
			'display_name': json.owner['display_name'],
			'reputation': json.owner['reputation'],
			'email_hash': json.owner['email_hash']})
		
		if hasattr(json, 'reply_to'):
			self.reply_to_user_id = json.reply_to['user_id']
			self.reply_to = User.partial(lambda self: self.site.user(self.id), site, {
				'id': self.reply_to_user_id,
				'user_type': Enumeration.from_string(json.reply_to['user_type'], UserType),
				'display_name': json.reply_to['display_name'],
				'reputation': json.reply_to['reputation'],
				'email_hash': json.reply_to['email_hash']})
		
		self.post_type = PostType.from_string(json.post_type)
	def get_post(self):
		if self.post_type == PostType.Question:
			return self.site.question(self.post_id)
		elif self.post_type == PostType.Answer:
			return self.site.answer(self.post_id)
	
	def __unicode__(self):
		return u'Comment ' + str(self.id)
	def __str__(self):
		return str(unicode(self))


##### Users ####
class Tag(JSONModel):
	transfer = ('name', 'count', 'user_id')

class BadgeType(Enumeration):
	"""Describes the rank or type of a badge: one of Bronze, Silver or Gold."""

	Bronze, Silver, Gold = range(3)

class Badge(JSONModel):
	"""Describes a badge awardable on a StackExchange site."""

	transfer = ('name', 'description', 'award_count', 'tag_based')
	def _extend(self, json, site):
		self.id = json.badge_id
		self.recipients = StackExchangeLazySequence(User, None, site, json.badges_recipients_url, self._up('recipients'))
	
	def __str__(self):
		return self.name

class RepChange(JSONModel):
	"""Describes an event which causes a change in reputation."""

	transfer = ('user_id', 'post_id', 'post_type', 'title', 'positive_rep', 'negative_rep')
	def _extend(self, json, site):
		self.on_date = datetime.date.fromtimestamp(json.on_date)
		self.score = self.positive_rep - self.negative_rep

## Timeline ##
class TimelineEvent(JSONModel):
	transfer = ('user_id', 'post_id', 'comment_id', 'action', 'description', 'detail')
	def _extend(self, json, site):
		self.timeline_type = TimelineEventType.from_string(json.timeline_type)
		self.post_type = PostType.from_string(json.post_type)
		self.creation_date = datetime.date.fromtimestamp(json.creation_date)
	
class TimelineEventType(Enumeration):
	"""Denotes the type of a timeline event."""
	_map = {'askoranswered': 'AskOrAnswered'}
	Comment, AskOrAnswered, Badge, Revision, Accepted = range(5)
##############

class PostType(Enumeration):
	"""Denotes the type of a post: a question or an answer."""

	Question, Answer = range(2)

class UserType(Enumeration):
	"""Denotes the status of a user on a site: whether it is Anonymous, Unregistered, Registered or a Moderator."""

	Anonymous, Unregistered, Registered, Moderator = range(4)

class User(JSONModel):
	"""Describes a user on a StackExchange site."""

	transfer = ('display_name', 'reputation', 'email_hash', 'age', 'website_url', 'location', 'about_me',
		'view_count', 'up_vote_count', 'down_vote_count')
	def _extend(self, json, site):
		self.id = json.user_id
		self.user_type = Enumeration.from_string(json.user_type, UserType)
		self.creation_date = datetime.date.fromtimestamp(json.creation_date)
		self.last_access_date = datetime.date.fromtimestamp(json.last_access_date)

		self.questions = StackExchangeLazySequence(Question, json.question_count, site, json.user_questions_url, self._up('questions'))
		self.answers = StackExchangeLazySequence(Answer, json.answer_count, site, json.user_answers_url, self._up('answers'))
# Grr, American spellings. Using them for consistency with official API.
		self.favorites = StackExchangeLazySequence(Question, None, site, json.user_favorites_url, self._up('favorites'), 'questions')
		self.tags = StackExchangeLazySequence(Tag, None, site, json.user_tags_url, self._up('tags'))
		self.badges = StackExchangeLazySequence(Badge, None, site, json.user_badges_url, self._up('badges'))
		self.timeline = StackExchangeLazySequence(TimelineEvent, None, site, json.user_timeline_url, self._up('timeline'), 'user_timelines')
		self.mentioned = StackExchangeLazySequence(Comment, None, site, json.user_mentioned_url, self._up('mentioned'), 'comments')
		self.comments = StackExchangeLazySequence(Comment, None, site, json.user_comments_url, self._up('comments'))
		self.reputation_detail = StackExchangeLazySequence(RepChange, None, site, json.user_reputation_url, self._up('reputation_detail'))

		self.vote_counts = (self.up_vote_count, self.down_vote_count)

		gold = json.badge_counts['gold'] if 'gold' in json.badge_counts else 0
		silver = json.badge_counts['silver'] if 'silver' in json.badge_counts else 0
		bronze = json.badge_counts['bronze'] if 'bronze' in json.badge_counts else 0
		self.badge_counts_t = (gold, silver, bronze)
		self.badge_counts = {
			BadgeType.Gold:   gold,
			BadgeType.Silver: silver,
			BadgeType.Bronze: bronze
		}
		self.gold_badges, self.silver_badges, self.bronze_badges = self.badge_counts_t
		self.badge_total = reduce(operator.add, self.badge_counts_t)
		
		self.url = 'http://' + self.site.root_domain + '/users/' + str(self.id)
	
	def __unicode__(self):
		return 'User %d [%s]' % (self.id, self.display_name)
	def __str__(self):
		return str(unicode(self))


class Site(object):
	"""Stores information and provides methods to access data on a StackExchange site. This class is the 'root' of the API - all data is accessed
through here."""

	def __init__(self, domain, app_key=None):
		self.domain = domain
		self.app_key = app_key
		self.api_version = '0.8'
		self.use_gzip = True

		self.include_body = False
		self.include_comments = False
		self.root_domain = '.'.join(self.domain.split('.')[1:])

	URL_Roots = {
		User: 'users/%s',
		Badge: 'badges/%s',
		Answer: 'answers/%s',
		Comment: 'comments/%s',
		Question: 'questions/%s',
	}
	
	def _kw_to_str(self, ob):
		try:
			if not isinstance(ob, str):
				i = iter(ob)
				return ';'.join(i)
			else:
				return ob
		except TypeError:
			return str(ob).lower()

	def _request(self, to, params):
		url = 'http://' + self.domain + '/' + self.api_version + '/' + to

		done = False
		for k, v in params.iteritems():
			if not done:
				url += '?'
				done = True
			else: url += '&'

			url += '%s=%s' % (k, self._kw_to_str(v))

		if self.app_key != None:
			url += ('?' if not '?' in url else '&') + 'key=' + self.app_key

		try:
			request = urllib2.Request(url)
			request.add_header('Accept-encoding', 'gzip')
			req_open = urllib2.build_opener()
			conn = req_open.open(request)

			req_data = conn.read()

			if self.use_gzip:
				data_stream = StringIO.StringIO(req_data)
				gzip_stream = gzip.GzipFile(fileobj=data_stream)
				actual_data = gzip_stream.read()
			else:
				actual_data = req_data

			dump = json.loads(actual_data)

			info = conn.info()
			self.rate_limit = (int(info.getheader('X-RateLimit-Current')), int(info.getheader('X-RateLimit-Max')))
			self.requests_used = self.rate_limit[1] - self.rate_limit[0]
			self.requests_left = self.rate_limit[0]

			conn.close()

			return dump
		except urllib2.URLError, e:
			raise StackExchangeError(e)
	
	def _user_prop(self, qs, typ, coll, kw, prop='user_id'):
		if prop not in kw:
			raise LookupError('No user ID provided.')
		else:
			tid = kw[prop]
			del kw[prop]

			return self.build('users/%d/%s' % (tid, qs), typ, coll, kw)

	def be_inclusive(self):
		"""Include the body and comments of a post, where appropriate, by default."""

		self.include_body, self.include_comments = True, True

	def build(self, url, typ, collection, kw={}):
		"""Builds a StackExchangeResultset object from the given URL and type."""

		if 'body' not in kw:
			kw['body'] = str(self.include_body).lower()
		if 'comments' not in kw:
			kw['comments'] = str(self.include_comments).lower()

		json = self._request(url, kw)
		
		if 'page' in json:
			# we have a paginated resultset
			page = json['page']
			pagesize = json['pagesize']
			items = []
	
			# create strongly-typed objects from the JSON items
			for json_item in json[collection]:
				json_item['_params_'] = kw	# convenient access to the kw hash
				items.append(typ(json_item, self))

			return StackExchangeResultset(items, page, pagesize, (self, url, typ, collection, kw))
		else:
			# this isn't a paginated resultset (unlikely, but possible - eg badges)
			return tuple([typ(x, self) for x in json[collection]])
	
	def build_from_snippet(self, json, typ):
		return StackExchangeResultSet([typ(x, self) for x in json])
	
	def _get(self, typ, ids, coll, kw):
		root = self.URL_Roots[typ] % ';'.join([str(x) for x in ids])
		return self.build(root, typ, coll, kw)

	def user(self, nid, **kw):
		"""Retrieves an object representing the user with the ID `nid`."""

		u, = self.users((nid,), **kw)
		return u
	
	def users(self, ids, **kw):
		"""Retrieves a list of the users with the IDs specified in the `ids' parameter."""
		return self._get(User, ids, 'users', kw)

	def answer(self, nid, **kw):
		"""Retrieves an object describing the answer with the ID `nid`."""

		a, = self.answers((nid,), **kw)
		return a
	
	def answers(self, ids=None, **kw):
		"""Retrieves a set of the answers with the IDs specified in the 'ids' parameter, or by the
		user_id specified."""
		if ids == None:
			return self._user_prop('answers', Answer, 'answers', kw)
		else:
			return self._get(Answer, ids, 'answers', kw)

	def comment(self, nid, **kw):
		"""Retrieves an object representing a comment with the ID `nid`."""
		c, = self.comments((nid,), **kw)
		return c
	
	def comments(self, ids=None, **kw):
		"""Retrieves a set of the comments with the IDs specified in the 'ids' parameter."""
		if ids == None:
			return self._user_prop('comments', Comment, 'comments', kw)
		else:
			return self._get(Comment, ids, 'comments', kw)
	
	def question(self, nid, **kw):
		"""Retrieves an object representing a question with the ID `nid`. Note that an answer ID can not be specified -
unlike on the actual site, you will receive an error rather than a redirect to the actual question."""
		q, = self.questions((nid,), **kw)
		return q
	
	def questions(self, ids=None, **kw):
		"""Retrieves a set of the comments with the IDs specified in the 'ids' parameter."""
		if 'answers' not in kw:
			kw['answers'] = 'true'
		if ids == None:
			return self._user_prop('questions', Question, 'questions', kw)
		else:
			return self._get(Question, ids, 'questions', kw)
	
	def recent_questions(self, **kw):
		"""Returns the set of the most recent questions on the site, by last activity."""
		if 'answers' not in kw:
			kw['answers'] = 'true'
		return self.build('questions', Question, 'questions', kw)
	
	def users_with_badge(self, bid, **kw):
		"""Returns the set of all the users who have been awarded the badge with the ID 'bid'."""
		return self.build('badges/' + str(bid), User, 'users', kw)
	
	def all_badges(self, **kw):
		"""Returns the set of all the badges which can be awarded on the site, excluding those which are awarded for specific tags."""
		return self.build('badges', Badge, 'badges', kw)
	
	def badges(self, ids=None, **kw):
		"""Returns the users with the badges with IDs."""
		if ids == None:
			return self._user_prop('badges', Badge, 'users', kw)
		else:
			return self._get(Badge, ids, 'users', kw)

	def badge(self, nid, **kw):
		"""Returns an object representing the badge with the ID 'nid'."""
		b, = self.badges((nid,), kw)
		return b
	
	def all_tag_badges(self, **kw):
		"""Returns the set of all the tag-based badges: those which are awarded for performance on a specific tag."""
		return self.build('badges/tags', Badge, 'badges', kw)
	
	def all_tags(self, **kw):
		return self.build('tags', Tag, 'tags', kw)
	
	def stats(self, **kw):
		return self.build('stats', Statistics, 'statistics', kw)[0]
