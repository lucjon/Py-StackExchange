import datetime, operator, time, urllib
from stackexchange.web import WebRequestManager
from stackexchange.core import *

# Site constants
from stackexchange.sites import *

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

		self.creation_date = datetime.datetime.fromtimestamp(json.creation_date)

		if hasattr(json, 'last_edit_date'):
			self.last_edit_date = datetime.datetime.fromtimestamp(json.last_edit_date)
		if hasattr(json, 'last_activity_date'):
			self.last_activity_date = datetime.datetime.fromtimestamp(json.last_activity_date)

		self.revisions = StackExchangeLazySequence(PostRevision, None, site, 'revisions/%s' % self.id, self._up('revisions'), 'revisions')
		self.votes = (self.up_vote_count, self.down_vote_count)
		self.url = 'http://' + self.site.root_domain + '/questions/' + str(self.question_id) + '/' + str(self.id) + '#' + str(self.id)

	def _get_user(self, id):
		if self._owner is None:
			self._owner = self.site.user(id)
		return self._owner

	def _set_user(self, ob):
		self._owner = ob

	def _get_quest(self, id):
		if self._question is None:
			self._question = self.site.question(id)
		return self._question

	def _set_quest(self, ob):
		self._question = ob

	question = property(_get_quest, _set_quest)
	owner = property(_get_user, _set_user)

	def fetch_callback(self, _, site):
		return site.answer(self.id)

	def __unicode__(self):
		return u'Answer %d [%s]' % (self.id, self.title)

	def __str__(self):
		return str(unicode(self))

	def __repr__(self):
		return '<Answer %d @ %x>' % (self.id, id(self))

class Question(JSONModel):
	"""Describes a question on a StackExchange site."""
	transfer = ('tags', 'favorite_count', 'up_vote_count', 'down_vote_count', 'view_count', 'score', 'community_owned', 'title', 'body', 'answer_count')

	def _extend(self, json, site):
		self.id = json.question_id

		self.timeline = StackExchangeLazySequence(TimelineEvent, None, site, json.question_timeline_url, self._up('timeline'))
		self.revisions = StackExchangeLazySequence(PostRevision, None, site, 'revisions/%s' % self.id, self._up('revisions'), 'revisions')

		self.creation_date = datetime.datetime.fromtimestamp(json.creation_date)
		if hasattr(json, 'last_activity_date'):
			self.last_activity_date = datetime.datetime.fromtimestamp(json.last_activity_date)

		self.comments_url = json.question_comments_url
		self.comments = StackExchangeLazySequence(Comment, None, site, self.comments_url, self._up('comments'))

		self.answers_url = json.question_answers_url

		if hasattr(json, 'answers'):
			self.answers = [Answer(x, site) for x in json.answers]
		else:
			self.answers = []

		if hasattr(json, 'accepted_answer_id'):
			self.accepted_answer_id = json.accepted_answer_id

		if hasattr(json, 'owner'):
			self.owner_id = json.owner['user_id']

			owner_dict = dict(json.owner)
			owner_dict['id'] = self.owner_id
			del owner_dict['user_id']
			owner_dict['user_type'] = UserType.from_string(owner_dict['user_type'])

			self.owner = User.partial(lambda self: self.site.user(self.id), site, owner_dict)

		self.url = 'http://' + self.site.root_domain + '/questions/' + str(self.id)

	def fetch_callback(self, _, site):
		return site.question(self.id)

	def linked(self):
		return self.site.questions(linked_to=self.id)

	def related(self):
		return self.site.questions(related_to=self.id)

	def __repr__(self):
		return "<Question '%s' @ %x>" % (self.title, id(self))

class Comment(JSONModel):
	"""Describes a comment to a question or answer on a StackExchange site."""

	transfer = ('post_id', 'score', 'edit_count', 'body')
	def _extend(self, json, site):
		self.id = json.comment_id

		self.creation_date = datetime.datetime.fromtimestamp(json.creation_date)

		if hasattr(json, 'owner'):
			self.owner_id = json.owner['owner_id'] if 'owner_id' in json.owner else json.owner['user_id']
			self.owner = User.partial(lambda self: self.site.user(self.id), site, {
				'id': self.owner_id,
				'user_type': Enumeration.from_string(json.owner['user_type'], UserType),
				'display_name': json.owner['display_name'],
				'reputation': json.owner['reputation'],
				'email_hash': json.owner['email_hash']})
		else:
			self.owner = None

		if hasattr(json, 'reply_to'):
			self.reply_to_user_id = json.reply_to['user_id']
			self.reply_to = User.partial(lambda self: self.site.user(self.id), site, {
				'id': self.reply_to_user_id,
				'user_type': Enumeration.from_string(json.reply_to['user_type'], UserType),
				'display_name': json.reply_to['display_name'],
				'reputation': json.reply_to['reputation'],
				'email_hash': json.reply_to['email_hash']})

		self.post_type = PostType.from_string(json.post_type)

	def _get_post(self):
		if self.post_type == PostType.Question:
			return self.site.question(self.post_id)
		elif self.post_type == PostType.Answer:
			return self.site.answer(self.post_id)
		else:
			return None

	post = property(_get_post)

	def __unicode__(self):
		return u'Comment ' + str(self.id)
	def __str__(self):
		return str(unicode(self))

#### Revisions #
class RevisionType(Enumeration):
	SingleUser = 'single_user'
	VoteBased  = 'vote_based'

class PostRevision(JSONModel):
	transfer = ('body', 'comment', 'is_question', 'is_rollback', 'last_body', 'last_title', 'revision_guid',
				'revision_number', 'title', 'set_community_wiki', 'post_id', 'last_tags', 'tags')

	def _extend(self, json, site):
		self.creation_date = datetime.datetime.fromtimestamp(json.creation_date)
		self.revision_type = RevisionType.from_string(json.revision_type)

		part = json.user
		self.user = User.partial(lambda self: self.site.user(self.id), site, {
			'id': part['user_id'],
			'user_type': Enumeration.from_string(part['user_type'], UserType),
			'display_name': part['display_name'],
			'reputation': part['reputation'],
			'email_hash': part['email_hash']
		})

	def _get_post(self):
		if self.is_question:
			return self.site.question(self.post_id)
		else:
			return self.site.answer(self.post_id)
	post = property(_get_post)

	# The SE API seems quite inconsistent in this regard; the other methods give a post_type in their JSON
	def _get_post_type(self):
		return PostType.Question if self.is_question else PostType.Answer
	post_type = property(_get_post_type)

	def __repr__(self):
		return '<Revision %d of %s%d>' % (self.revision_number, 'Q' if self.is_question else 'A', self.post_id)

##### Tags #####
class TagSynonym(JSONModel):
	transfer = ('from_tag', 'to_tag', 'applied_count')

	def _extend(self, json, site):
		self.creation_date = datetime.datetime.fromtimestamp(json.creation_date)
		self.last_applied_date = datetime.datetime.fromtimestamp(json.last_applied_date)

	def __repr__(self):
		return "<TagSynonym '%s'->'%s'>" % (self.from_tag, self.to_tag)

class TagWiki(JSONModel):
	transfer = ('tag_name')

	def _extend(self, json, site):
		self.body = json.wiki_body
		self.excerpt = json.wiki_excerpt
		self.body_last_edit_date = datetime.datetime.fromtimestamp(json.body_last_edit_date)
		self.excerpt_last_edit_date = datetime.datetime.fromtimestamp(json.excerpt_last_edit_date)

		body_editor = dict(json.last_body_editor)
		body_editor['id'] = body_editor['user_id']
		del body_editor['user_id']
		self.last_body_editor = User.partial(lambda s: s.site.user(self.id), site, body_editor)

		excerpt_editor = dict(json.last_excerpt_editor)
		excerpt_editor['id'] = excerpt_editor['user_id']
		del excerpt_editor['user_id']
		self.last_excerpt_editor = User.partial(lambda s: s.site.user(self.id), site, excerpt_editor)

class Period(Enumeration):
	AllTime, Month = 'all-time', 'month'

class TopUser(JSONModel):
	transfer = ('score', 'post_count')

	def _extend(self, json, site):
		user_dict = dict(json.user)
		user_dict['id'] = user_dict['user_id']
		del user_dict['user_id']
		self.user = User.partial(lambda self: self.site.user(self.id), site, user_dict)

	def __repr__(self):
		return "<TopUser '%s' (score %d)>" % (self.user.display_name, self.score)

class Tag(JSONModel):
	transfer = ('name', 'count', 'fulfills_required')
	# Hack so that Site.vectorise() works correctly
	id = property(lambda self: self.name)

	def _extend(self, json, site):
		self.synonyms = StackExchangeLazySequence(TagSynonym, None, site, 'tags/%s/synonyms' % self.name, self._up('synonyms'), 'tag_synonyms')
		self.wiki = StackExchangeLazyObject(TagWiki, site, 'tags/%s/wikis' % self.name, self._up('wiki'), 'tag_wikis')

	def top_askers(self, period, **kw):
		return self.site.build('tags/%s/top-askers/%s' % (self.name, period), TopUser, 'top_users', kw)

	def top_answerers(self, period, **kw):
		return self.site.build('tags/%s/top-answerers/%s' % (self.name, period), TopUser, 'top_users', kw)

##### Users ####
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
	def __repr__(self):
		return '<Badge \'%s\' @ %x>' % (self.name, id(self))

class RepChange(JSONModel):
	"""Describes an event which causes a change in reputation."""

	transfer = ('user_id', 'post_id', 'post_type', 'title', 'positive_rep', 'negative_rep')
	def _extend(self, json, site):
		self.on_date = datetime.datetime.fromtimestamp(json.on_date)
		self.score = self.positive_rep - self.negative_rep

## Timeline ##
class TimelineEventType(Enumeration):
	"""Denotes the type of a timeline event."""
	_map = {'askoranswered': 'AskOrAnswered'}

	Comment = 'comment'
	AskOrAnswered = 'askoranswered'
	Badge = 'badge'
	Revision = 'revision'
	Accepted = 'accepted'

class TimelineEvent(JSONModel):
	transfer = ('user_id', 'post_id', 'comment_id', 'action', 'description', 'detail', 'comment_id')
	_post_related = (TimelineEventType.AskOrAnswered, TimelineEventType.Revision, TimelineEventType.Comment)

	def _extend(self, json, site):
		self.timeline_type = TimelineEventType.from_string(json.timeline_type)

		if self.timeline_type in self._post_related:
			self.post_type = PostType.from_string(json.post_type)
			self.creation_date = datetime.datetime.fromtimestamp(json.creation_date)

	def _get_post(self):
		if self.timeline_type in self._post_related:
			if self.post_type == PostType.Question:
				return self.site.question(self.post_id)
			else:
				return self.site.answer(self.post_id)
		else:
			return None

	def _get_comment(self):
		if self.timeline_type == TimelineEventType.Comment:
			return self.site.comment(self.comment_id)
		else:
			return None

	def _get_badge(self):
		if self.timeline_type == TimelineEventType.Badge:
			return self.site.badge(name=self.description)
		else:
			return None

	post = property(_get_post)
	comment = property(_get_comment)
	badge = property(_get_badge)

##############

class PostType(Enumeration):
	"""Denotes the type of a post: a question or an answer."""
	Question, Answer = 'question', 'answer'

class UserType(Enumeration):
	"""Denotes the status of a user on a site: whether it is Anonymous, Unregistered, Registered or a Moderator."""
	Anonymous = 'anonymous'
	Registered = 'registered'
	Unregistered = 'unregistered'
	Moderator = 'moderator'

class FormattedReputation(int):
	def format(rep):
		"""Formats the reputation score like it is formatted on the sites. Heavily based on CMS' JavaScript implementation at
		http://stackapps.com/questions/1012/how-to-format-reputation-numbers-similar-to-stack-exchange-sites/1019#1019"""
		str_rep = str(rep)

		if rep < 1000:
			return str_rep
		elif rep < 10000:
			return '%s,%s' % (str_rep[0], str_rep[1:])
		elif rep % 1000 == 0:
			return '%dk' % (rep / 1000.0)
		else:
			return '%.1fk' % (rep / 1000.0)

class TopTag(JSONModel):
	transfer = ('tag_name', 'question_score', 'question_count', 'answer_score', 'answer_count')

	def __repr__(self):
		return "<TopTag '%s' Q:%d A:%d>" % (self.tag_name, self.question_score, self.answer_score)

class User(JSONModel):
	"""Describes a user on a StackExchange site."""

	transfer = ('display_name', 'email_hash', 'age', 'website_url', 'location', 'about_me',
		'view_count', 'up_vote_count', 'down_vote_count', 'association_id')
	def _extend(self, json, site):
		self.id = json.user_id
		self.type = Enumeration.from_string(json.user_type, UserType)
		self.creation_date = datetime.datetime.fromtimestamp(json.creation_date)
		self.last_access_date = datetime.datetime.fromtimestamp(json.last_access_date)
		self.reputation = FormattedReputation(json.reputation)

		self.questions = StackExchangeLazySequence(Question, json.question_count, site, json.user_questions_url, self._up('questions'))
		self.no_answers_questions = StackExchangeLazySequence(Question, None, site, 'users/%d/questions/no-answers' % self.id, self._up('no_answers_questions'), 'questions')
		self.unanswered_questions = StackExchangeLazySequence(Question, None, site, 'users/%d/questions/unanswered' % self.id, self._up('unanswered_questions'), 'questions')
		self.unaccepted_questions = StackExchangeLazySequence(Question, None, site, 'users/%d/questions/unaccepted' % self.id, self._up('unaccepted_questions'), 'questions')
		self.favorites = StackExchangeLazySequence(Question, None, site, json.user_favorites_url, self._up('favorites'), 'questions')

		self.answers = StackExchangeLazySequence(Answer, json.answer_count, site, json.user_answers_url, self._up('answers'))
		# Grr, American spellings. Using them for consistency with official API.
		self.tags = StackExchangeLazySequence(Tag, None, site, json.user_tags_url, self._up('tags'))
		self.badges = StackExchangeLazySequence(Badge, None, site, json.user_badges_url, self._up('badges'))
		self.timeline = StackExchangeLazySequence(TimelineEvent, None, site, json.user_timeline_url, self._up('timeline'), 'user_timelines')
		self.reputation_detail = StackExchangeLazySequence(RepChange, None, site, json.user_reputation_url, self._up('reputation_detail'))

		self.mentioned = StackExchangeLazySequence(Comment, None, site, json.user_mentioned_url, self._up('mentioned'), 'comments')
		self.comments = StackExchangeLazySequence(Comment, None, site, json.user_comments_url, self._up('comments'))
		self.mentioned = StackExchangeLazySequence(Comment, None, site, 'users/%d/mentioned' % self.id, self._up('mentioned'))

		self.top_answer_tags = StackExchangeLazySequence(TopTag, None, site, 'users/%d/top-answer-tags' % self.id, self._up('top_answer_tags'), 'top_tags')
		self.top_question_tags = StackExchangeLazySequence(TopTag, None, site, 'users/%d/top-question-tags' % self.id, self._up('top_question_tags'), 'top_tags')

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
		self.is_moderator = self.type == UserType.Moderator

		self.url = 'http://' + self.site.root_domain + '/users/' + str(self.id)

	def has_privelege(self, privelege):
		return self.reputation >= privelege.reputation

	def _get_real_tag(self, tag):
		return tag.name if isinstance(tag, Tag) else tag

	def top_answers_in_tag(self, tag, **kw):
		return self.site.build('users/%d/tags/%s/top-answers' % (self.id, self._get_real_tag(tag)), Answer, 'answers', kw)

	def top_questions_in_tag(self, tag, **kw):
		return self.site.build('users/%d/tags/%s/top-questions' % (self.id, self._get_real_tag(tag)), Question, 'questions', kw)

	def comments_to(self, user, **kw):
		uid = user.id if isinstance(user, User) else user
		return self.site.build('users/%d/comments/%d' % (self.id, uid), Comment, 'comments' ,kw)

	def __unicode__(self):
		return 'User %d [%s]' % (self.id, self.display_name)
	def __str__(self):
		return str(unicode(self))
	def __repr__(self):
		return "<User '%s' (%d) @ %x>" % (self.display_name, self.id, id(self))

class Privelege(JSONModel):
	transfer = ('short_description', 'description', 'reputation')


class QuestionsQuery(object):
	def __init__(self, site):
		self.site = site

	def check(self, kw):
		if 'answers' not in kw:
			kw['answers'] = 'true'
		if self.site.include_body:
			kw['body'] = 'true'
		if self.site.include_comments:
			kw['comments'] = 'true'

	def __call__(self, ids=None, user_id=None, **kw):
		self.check(kw)

		# Compatibility hack, as user_id= was in versions below v1.1
		if ids is None and user_id is not None:
			return self.by_user(user_id, **kw)
		elif ids is None and user_id is None:
			return self.site.build('questions', Question, 'questions', kw)
		else:
			return self.site._get(Question, ids, 'questions', kw)

	def linked_to(self, qn, **kw):
		self.check(kw)
		url = 'questions/%s/linked' % self.site.vectorise(qn, Question)
		return self.site.build(url, Question, 'questions', kw)

	def related_to(self, qn, **kw):
		self.check(kw)
		url = 'questions/%s/related' % self.site.vectorise(qn, Question)
		return self.site.build(url, Question, 'questions', kw)

	def by_user(self, usr, **kw):
		self.check(kw)
		kw['user_id'] = usr
		return self.site._user_prop('questions', Question, 'questions', kw)

	def unanswered(self, by=None, **kw):
		self.check(kw)

		if by is None:
			return self.site.build('questions/unanswered', Question, 'questions', kw)
		else:
			kw['user_id'] = by
			return self.site._user_prop('questions/unanswered', Question, 'questions', kw)

	def no_answers(self, by=None, **kw):
		self.check(kw)

		if by is None:
			return self.site.build('questions/no-answers', Question, 'questions', kw)
		else:
			kw['user_id'] = by
			return self.site._user_prop('questions/no-answers', Question, 'questions', kw)

	def unaccepted(self, by, **kw):
		self.check(kw)
		kw['user_id'] = by
		return self.site._user_prop('questions/unaccepted', Questions, 'questions', kw)

	def favorited_by(self, by, **kw):
		self.check(kw)
		kw['user_id'] = by
		return self.site._user_prop('favorites', Question, 'questions', kw)

class Site(object):
	"""Stores information and provides methods to access data on a StackExchange site. This class is the 'root' of the API - all data is accessed
through here."""

	def __init__(self, domain, app_key=None, cache=1800):
		self.domain = domain
		self.app_key = app_key
		self.api_version = '1.1'

		self.impose_throttling = False
		self.throttle_stop = True
		self.cache_options = {'cache': False} if cache == 0 else {'cache': True, 'cache_age': cache}

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
			if isinstance(ob, datetime.datetime):
				return str(time.mktime(ob.timetuple()))
			elif isinstance(ob, basestring):
				return ob
			else:
				i = iter(ob)
				return ';'.join(i)
		except TypeError:
			return str(ob).lower()

	def _request(self, to, params):
		url = 'http://' + self.domain + '/' + self.api_version + '/' + to

		new_params = {}
		for k, v in params.iteritems():
			if k in ('fromdate', 'todate'):
				# bit of a HACKish workaround for a reported issue; force to an integer
				new_params[k] = str(int(v))
			else:
				new_params[k] = self._kw_to_str(v)
		if self.app_key != None:
			new_params['key'] = self.app_key

		request_properties = dict([(x, getattr(self, x)) for x in ('impose_throttling', 'throttle_stop')])
		request_properties.update(self.cache_options)
		request_mgr = WebRequestManager(**request_properties)

		json, info = request_mgr.json_request(url, new_params)

		self.rate_limit = (int(info.getheader('X-RateLimit-Current')), int(info.getheader('X-RateLimit-Max')))
		self.requests_used = self.rate_limit[1] - self.rate_limit[0]
		self.requests_left = self.rate_limit[0]

		return json

	def _user_prop(self, qs, typ, coll, kw, prop='user_id'):
		if prop not in kw:
			raise LookupError('No user ID provided.')
		else:
			tid = self.vectorise(kw[prop], User)
			del kw[prop]

			return self.build('users/%s/%s' % (tid, qs), typ, coll, kw)

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
		return JSONMangler.json_to_resultset(self, json, typ, collection, (self, url, typ, collection, kw))

	def build_from_snippet(self, json, typ):
		return StackExchangeResultSet([typ(x, self) for x in json])

	def vectorise(self, lst, or_of_type=None):
		# Ensure we're always dealing with an iterable
		allowed_types = or_of_type
		if allowed_types is not None and not hasattr(allowed_types, '__iter__'):
			allowed_types = (allowed_types, )

		if hasattr(lst, '__iter__'):
			return ';'.join([self.vectorise(x, or_of_type) for x in lst])
		elif allowed_types is not None and any([isinstance(lst, typ) for typ in allowed_types]) and hasattr(lst, 'id'):
			return str(lst.id)
		elif isinstance(lst, basestring):
			return lst
		else:
			return str(lst).lower()

	def _get(self, typ, ids, coll, kw):
		root = self.URL_Roots[typ] % self.vectorise(ids)
		return self.build(root, typ, coll, kw)


	def user(self, nid, **kw):
		"""Retrieves an object representing the user with the ID `nid`."""
		u, = self.users((nid,), **kw)
		return u

	def users(self, ids=[], **kw):
		"""Retrieves a list of the users with the IDs specified in the `ids' parameter."""
		return self._get(User, ids, 'users', kw)

	def users_by_name(self, name, **kw):
		kw['filter'] = name
		return self.users(**kw)

	def moderators(self, **kw):
		"""Retrieves a list of the moderators on the site."""
		return self.build('users/moderators', User, 'users', kw)

	def answer(self, nid, **kw):
		"""Retrieves an object describing the answer with the ID `nid`."""
		a, = self.answers((nid,), **kw)
		return a

	def answers(self, ids=None, **kw):
		"""Retrieves a set of the answers with the IDs specified in the 'ids' parameter, or by the
		user_id specified."""
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

	def comments(self, ids=None, posts=None, **kw):
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

	def badge(self, nid, name=None, **kw):
		"""Returns an object representing the badge with the ID 'nid', or with the name passed in as name=."""
		if name is None:
			b, = self.badges((nid,), kw)
			return b
		else:
			# We seem to need to get all badges and find it by name. Sigh.
			all_badges = self.badges()
			for badge in all_badges:
				if badge.name == name:
					return badge
			return None

	def privileges(self):
		"""Returns all the privileges a user can have on the site."""
		return self.build('privileges', Privelege, 'privileges', kw)

	def all_nontag_badges(self, **kw):
		"""Returns the set of all badges which are not tag-based."""
		return self.build('badges/name', Badge, 'badges', kw)

	def all_tag_badges(self, **kw):
		"""Returns the set of all the tag-based badges: those which are awarded for performance on a specific tag."""
		return self.build('badges/tags', Badge, 'badges', kw)

	def all_tags(self, **kw):
		'''Returns the set of all tags on the site.'''
		return self.build('tags', Tag, 'tags', kw)

	def stats(self, **kw):
		'''Returns statistical information on the site, such as number of questions.'''
		return self.build('stats', Statistics, 'statistics', kw)[0]

	def revision(self, post, guid, **kw):
		real_id = post.id if isinstance(post, Question) or isinstance(post, Answer) else post
		return self.build('revisions/%d/%s' % (real_id, guid), PostRevision, 'revisions', kw)[0]

	def revisions(self, post, **kw):
		return self.build('revisions/' + self.vectorise(post, (Question, Answer)), PostRevision, 'revisions', kw)

	def search(self, **kw):
		return self.build('search', Question, 'questions', kw)

	def similar(self, title, tagged=None, nottagged=None, **kw):
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
		kw['filter'] = tag
		return self.build('tags', Tag, 'tags', kw)[0]

	def tag_synonyms(self, **kw):
		return self.build('tags/synonyms', TagSynonym, 'tag_synonyms', kw)

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
