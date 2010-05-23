import urllib2, json, httplib, datetime, operator

# Site constants
StackOverflow = 'api.stackoverflow.com'
SuperUser = 'api.superuser.com'
ServerFault = 'api.serverfault.com'
### Broken for now ###
StackApps = 'api.stackapps.com'
MetaStackOverflow = 'api.meta.stackoverflow.com'

#### Hack, because I can't be bothered to fix my mistaking JSON's output for an object not a dict
# Attrib: Eli Bendersky, http://stackoverflow.com/questions/1305532/convert-python-dict-to-object/1305663#1305663
class DictObject:
    def __init__(self, **entries): 
        self.__dict__.update(entries)

class StackExchangeError(Exception):
	def __init__(self, urlerror):
		self.urlerror = urlerror
	def __str__(self):
		return 'Received HTTP error \'%d\'.' % self.urlerror.code

class StackExchangeResultset(tuple):
	def __new__(cls, items, page, pagesize):
		ob = tuple(items)
		return ob
	def __init__(self, items, page, pagesize):
		self.page = page
		self.pagesize = pagesize

class Enumeration(object):
	@classmethod
	def from_string(cls, text, typ=None):
		if typ is not None:
			return getattr(typ, text[0].upper() + text[1:])
		else:
			return cls.from_string(text, cls)

##### Lazy Collections ###
class LazyTimeline(object):
	def __init__(self, user, url, fetched):
		self.url = url
		self.user = user
		self.fetched = fetched

class NeedsAwokenError(Exception):
	def __init__(self, lazy):
		self.lazy = lazy
	def __str__(self):
		return 'Could not return requested data; the sequence of "%s" has not been fetched.' % self.lazy.m_lazy

class StackExchangeLazySequence(list):
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
	
	def fetch(self):
		res = self.site.build(self.url, self.m_type, self.collection)
		if self.fetch_callback != None:
			self.fetch_callback(res)
		return res

## JSONModel base class
class JSONModel(object):
	def __init__(self, json, site, skip_ext=False):
		self.json_ob = DictObject(**json)
		self.site = site

		for f in [x for x in self.transfer if hasattr(self.json_ob, x)]:
			setattr(self, f, getattr(self.json_ob, f))

		if hasattr(self, '_extend') and not skip_ext:
			self._extend(self.json_ob, site)

	def fetch(self):
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
		model = cls({}, site, True)
		
		for k, v in populate.iteritems():
			setattr(model, k, v)

		model.fetch_callback = fetch_callback

	# for use with Lazy classes that need a callback to actually set the model property
	def _up(self, a):
		def inner(m):
			setattr(self, a, m)
		return inner

##### Content Types ###
class Answer(JSONModel):
	transfer = ('accepted', 'locked_date', 'question_id', 'up_vote_count', 'down_vote_count', 'view_count', 'score',
		'community_owned', 'title', 'body')

	def _extend(self, json, site):
		self.id = json.answer_id
		self.comments = site.build_from_snippet(json.comments, Comment) if ('comment' in json._params_ and json._params_['comment']) else StackExchangeLazySequence(Comment, None, site, json.answer_comments_url, self._up('comments'))

		self._question, self._owner = None, None
		self.owner_id = json.owner['user_id']
		self.owner_info = tuple(json.owner.values())

		self.creation_date = datetime.date.fromtimestamp(json.creation_date)

		if hasattr(json, 'last_edit_date'):
			self.last_edit_date = datetime.date.fromtimestamp(json.last_edit_date)
		if hasattr(json, 'last_activity_date'):
			self.last_activity_date = datetime.date.fromtimestamp(json.last_activity_date)

		self.votes = (self.up_vote_count, self.down_vote_count)
	
	question = property(lambda self: self._question if self._question is not None else self.site.question(self.qustion_id))
	owner = property(lambda self: self._owner if self._owner is not None else self.site.user(self.owner_id))

class Question(object):
	pass

class Comment(JSONModel):
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


##### Users ####
class Mention(object):
	pass

class Tag(object):
	pass

class Favorite(object):
	pass

class BadgeType(Enumeration):
	Bronze, Silver, Gold = range(3)

class Badge(object):
	pass

class RepChange(object):
	pass

class PostType(Enumeration):
	Question, Answer = range(2)

class UserType(Enumeration):
	Anonymous, Unregistered, Registered, Moderator = range(4)

class User(JSONModel):
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
		self.favorites = StackExchangeLazySequence(Favorite, None, site, json.user_favorites_url, self._up('favorites'))
		self.tags = StackExchangeLazySequence(Tag, None, site, json.user_tags_url, self._up('tags'))
		self.badges = StackExchangeLazySequence(Badge, None, site, json.user_badges_url, self._up('badges'))
		self.timeline = LazyTimeline(self, json.user_timeline_url, self._up('timeline'))
		self.mentioned = StackExchangeLazySequence(Mention, None, site, json.user_mentioned_url, self._up('mentioned'))
		self.comments = StackExchangeLazySequence(Comment, None, site, json.user_comments_url, self._up('comments'))
		self.reputation_detail = StackExchangeLazySequence(RepChange, None, site, json.user_reputation_url, self._up('reputation_detail'))

		self.vote_counts = (self.up_vote_count, self.down_vote_count)
		self.badge_counts_t = (json.badge_counts['gold'], json.badge_counts['silver'], json.badge_counts['bronze'])
		self.badge_counts = {
			BadgeType.Gold: json.badge_counts['gold'],
			BadgeType.Silver: json.badge_counts['silver'],
			BadgeType.Bronze: json.badge_counts['bronze']
		}
		self.gold_badges, self.silver_badges, self.bronze_badges = self.badge_counts_t
		self.badge_total = reduce(operator.add, self.badge_counts_t)


class Site(object):
	def __init__(self, domain, app_key=None):
		self.domain = domain
		self.app_key = app_key
		self.api_version = '0.8'

		self.include_body = False
		self.include_comments = False
	
	URL_Roots = {
		User: 'users/%s',
		Answer: 'answers/%s',
		Comment: 'comments/%s',
	}
	
	def _request(self, to, params):
		url = 'http://' + self.domain + '/' + self.api_version + '/' + to

		done = False
		for k, v in params.iteritems():
			if not done:
				url += '?'
				done = True
			else: url += '&'

			url += '%s=%s' % (k, str(v))

		if self.app_key != None:
			if not '?' in url:
				url += '?key=appkey'
			else:
				url += '&key=appkey'

		try:
			conn = urllib2.urlopen(url)
			dump = json.load(conn)
			conn.close()

			return dump
		except urllib2.URLError, e:
			raise StackExchangeError(e)
	
	def be_inclusive(self):
		self.include_body, self.include_comments = True, True

	def build(self, url, typ, collection, kw={}):
		"""Builds a StackExchangeResultset object from the given URL and type."""
		if 'body' not in kw:
			kw['body'] = str(self.include_body)
		if 'comments' not in kw:
			kw['comments'] = str(self.include_comments)

		json = self._request(url, kw)
		page = json['page']
		pagesize = json['pagesize']
		items = []

		# create strongly-typed objects from the JSON items
		for json_item in json[collection]:
			json_item['_params_'] = kw	# convenient access to the kw hash
			items.append(typ(json_item, self))

		return StackExchangeResultset(items, page, pagesize)
	
	def build_from_snippet(self, json, typ):
		return StackExchangeResultSet([typ(x, self) for x in json])
	
	def user(self, nid, **kw):
		"""Retrieves an object representing the user with the ID `nid`."""
		u, = self.users((nid,), **kw)
		return u
	
	def users(self, ids, **kw):
		"""Retrieves a list of the users with the IDs specified in the `ids' parameter."""
		root = self.URL_Roots[User] % ';'.join([str(x) for x in ids])
		return self.build(root, User, 'users', kw)

	def answer(self, nid, **kw):
		a, = self.answers((nid,), **kw)
		return a
	
	def answers(self, ids, **kw):
		root = self.URL_Roots[Answer] % ';'.join([str(x) for x in ids])
		return self.build(root, Answer, 'answers', kw)

	def comment(self, nid, **kw):
		c, = self.comments((nid,), **kw)
		return c
	
	def comments(self, ids, **kw):
		root = self.URL_Roots[Comment] % ';'.join([str(x) for x in ids])
		return self.build(root, Comment, 'comments', kw)
