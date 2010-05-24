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
    def __init__(self, entries): 
        self.__dict__.update(entries)

class StackExchangeError(Exception):
	def __init__(self, urlerror):
		self.urlerror = urlerror
	def __str__(self):
		return 'Received HTTP error \'%d\'.' % self.urlerror.code

class StackExchangeResultset(tuple):
	def __new__(cls, items, page, pagesize, build_info):
		cls.page, cls.pagesize, cls.build_info = page, pagesize, build_info
		return tuple.__new__(cls, items)
	
	def reload(self):
		# kind of a cheat, but oh well
		return self.fetch_page(self.page)

	def fetch_page(self, page):
		new_params = list(self.build_info)
		new_params[4] = new_params[4].copy()
		new_params[4]['page'] = page
		return new_params[0].build(*new_params[1:])
	
	def fetch_extended(self, page):
		next = self.fetch_page(page)
		extended = self + next

		# max(0, ...) is so a non-zero, positive result for page is always found
		return StackExchangeResultset(extended, max(1, self.page - 1), self.pagesize + next.pagesize, self.build_info)

	def fetch_next(self):
		return self.fetch_page(self.page + 1)
	
	def extend_next(self):
		return self.fetch_extended(self.page + 1)

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
		self.json_ob = DictObject(json)
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
	
	question = property(lambda self: self._question if self._question is not None else self.site.question(self.qustion_id))
	owner = property(lambda self: self._owner if self._owner is not None else self.site.user(self.owner_id))

	def __unicode__(self):
		return u'Answer %d [%s]' % (self.id, self.title)
	def __str__(self):
		return str(unicode(self))

class Question(JSONModel):
	transfer = ('tags', 'favorite_count', 'up_vote_count', 'down_vote_count', 'view_count', 'score', 'community_owned', 'title', 'body')

	def _extend(self, json, site):
		self.id = json.question_id

		self.timeline = LazyTimeline(self, json.question_timeline_url, self._up('timeline'))

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
	
	def __unicode__(self):
		return u'Comment ' + str(self.id)
	def __str__(self):
		return str(unicode(self))


##### Users ####
class Mention(object):
	pass

class Tag(object):
	pass

class Favorite(object):
	pass

class BadgeType(Enumeration):
	Bronze, Silver, Gold = range(3)

class Badge(JSONModel):
	transfer = ('name', 'description', 'award_count', 'tag_based')
	def _extend(self, json, site):
		self.id = json.badge_id
		self.recipients = StackExchangeLazySequence(User, None, site, json.badges_recipients_url, self._up('recipients'))

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
	
	def __unicode__(self):
		return 'User %d [%s]' % (self.id, self.display_name)
	def __str__(self):
		return str(unicode(self))


class Site(object):
	def __init__(self, domain, app_key=None):
		self.domain = domain
		self.app_key = app_key
		self.api_version = '0.8'

		self.include_body = False
		self.include_comments = False
	
	URL_Roots = {
		User: 'users/%s',
		Badge: 'badges/%s',
		Answer: 'answers/%s',
		Comment: 'comments/%s',
		Question: 'questions/%s',
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
			url += ('?' if not '?' in url else '&') + 'key=' + self.app_key

		try:
			conn = urllib2.urlopen(url)
			dump = json.load(conn)

			info = conn.info()
			self.rate_limit = (int(info.getheader('X-RateLimit-Current')), int(info.getheader('X-RateLimit-Max')))
			self.requests_left = self.rate_limit[1] - self.rate_limit[0]

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
		a, = self.answers((nid,), **kw)
		return a
	
	def answers(self, ids, **kw):
		return self._get(Answer, ids, 'answers', kw)

	def comment(self, nid, **kw):
		c, = self.comments((nid,), **kw)
		return c
	
	def comments(self, ids, **kw):
		return self._get(Comment, ids, 'comments', kw)
	
	def question(self, nid, **kw):
		q, = self.questions((nid,), **kw)
		return q
	
	def questions(self, ids, **kw):
		return self._get(Question, ids, 'questions', kw)
	
	def recent_questions(self, **kw):
		return self.build('questions', Question, 'questions', kw)
	
	def users_with_badge(self, bid, **kw):
		return self.build('badges/' + str(bid), User, 'users', kw)
	
	def all_badges(self, **kw):
		return self.build('badges', Badge, 'badges', kw)
	
	def badges(self, ids, **kw):
		return self._get(Badge, ids, 'badges', kw)

	def badge(self, nid, **kw):
		b, = self.badges((nid,), kw)
		return b
	
	def all_tag_badges(self, **kw):
		return self.build('badges/tags', Badge, 'badges', kw)
