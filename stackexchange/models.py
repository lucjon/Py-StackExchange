import re, sys
from stackexchange.core import *

LaterClass = lambda name: LaterClassIn(name, sys.modules[__name__])

#### Revisions #
class RevisionType(Enumeration):
    SingleUser = 'single_user'
    VoteBased  = 'vote_based'

class PostRevision(JSONModel):
    transfer = ('body', 'comment', 'is_question', 'is_rollback', 'last_body',
        'last_title', 'revision_guid', 'revision_number', 'title',
        'set_community_wiki', 'post_id', 'last_tags', 'tags',
        ('creation_date', UNIXTimestamp),
        ('revision_type', RevisionType.from_string))

    def _extend(self, json, site):
        part = json.user
        self.user = User.partial(lambda self: self.site.user(self.id), site, {
            'id': part['user_id'],
            'user_type': Enumeration.from_string(part['user_type'], UserType),
            'display_name': part['display_name'],
            'reputation': part['reputation'],
            'profile_image': part['profile_image']
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

class PostType(Enumeration):
    """Denotes the type of a post: a question or an answer."""
    Question, Answer = 'question', 'answer'

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
    transfer = ('user_id', 'post_id', 'comment_id', 'action', 'description',
        'detail', 'comment_id',
        ('timeline_type', TimelineEventType.from_string),
        ('post_type', PostType.from_string),
        ('creation_date', UNIXTimestamp))

    _post_related = (TimelineEventType.AskOrAnswered, TimelineEventType.Revision, TimelineEventType.Comment)
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
            return self.site.badge(name = self.description)
        else:
            return None

    post = property(_get_post)
    comment = property(_get_comment)
    badge = property(_get_badge)


##### Content Types ###
class Comment(JSONModel):
    """Describes a comment to a question or answer on a StackExchange site."""
    transfer = ('post_id', 'score', 'edit_count', 'body',
        ('creation_date', UNIXTimestamp), ('post_type', PostType.from_string))

    def _extend(self, json, site):
        self.id = json.comment_id

        if hasattr(json, 'owner'):
            self.owner_id = json.owner['owner_id'] if 'owner_id' in json.owner else json.owner['user_id']
            self.owner = User.partial(lambda self: self.site.user(self.id), site, {
                'id': self.owner_id,
                'user_type': Enumeration.from_string(json.owner['user_type'], UserType),
                'display_name': json.owner['display_name'],
                'reputation': json.owner['reputation'],
                'profile_image': json.owner['profile_image']})
        else:
            self.owner = None

        if hasattr(json, 'reply_to'):
            self.reply_to_user_id = json.reply_to['user_id']
            self.reply_to = User.partial(lambda self: self.site.user(self.id), site, {
                'id': self.reply_to_user_id,
                'user_type': Enumeration.from_string(json.reply_to['user_type'], UserType),
                'display_name': json.reply_to['display_name'],
                'reputation': json.reply_to['reputation'],
                'profile_image': json.reply_to['profile_image']})

    @property
    def post(self):
        if self.post_type == PostType.Question:
            return self.site.question(self.post_id)
        elif self.post_type == PostType.Answer:
            return self.site.answer(self.post_id)
        else:
            return None

    def __unicode__(self):
        return u'Comment ' + str(self.id)
    def __str__(self):
        return str(unicode(self))

class Answer(JSONModel):
    """Describes an answer on a StackExchange site."""

    transfer = ('is_accepted', 'locked_date', 'question_id', 'up_vote_count',
        'down_vote_count', 'view_count', 'score', 'community_owned', 'title',
        'body', 'body_markdown', ('creation_date', UNIXTimestamp),
        ('last_edit_date', UNIXTimestamp),
        ('last_activity_date', UNIXTimestamp),
        ('revisions', LazySequenceField(PostRevision, 'posts/{id}/revisions')))
    alias = (('id', 'answer_id'), ('accepted', 'is_accepted'))

    def _extend(self, json, site):
        if not hasattr(json, '_params_'):
            comment = False
        else:
            comment = ('comment' in json._params_ and json._params_['comment'])

        answer_comments_url = 'answers/%d/comments' % self.id
        self.comments = site.build_from_snippet(json.comments, Comment) if comment else StackExchangeLazySequence(Comment, None, site, answer_comments_url, self._up('comments'), filter = '!-*7AsUyrEan0')

        self._question, self._owner = None, None
        if hasattr(json, 'owner'):
            self.owner_id = json.owner.get('user_id')
            self.owner_info = tuple(json.owner.values())

        if hasattr(self, 'up_vote_count') and hasattr(self, 'down_vote_count'):
            self.votes = (self.up_vote_count, self.down_vote_count)

        self.url = 'http://' + self.site.root_domain + '/questions/' + str(self.question_id) + '/' + str(self.id) + '#' + str(self.id)

    @property
    def owner(self):
        if self._owner is None:
            self._owner = self.site.user(self.owner_id)
        return self._owner
    
    @property
    def question(self):
        if self._question is None:
            self._question = self.site.question(self.question_id)
        return self._question

    def fetch_callback(self, _, site):
        return site.answer(self.id)

    def __unicode__(self):
        return u'Answer %d' % self.id

    def __str__(self):
        return str(unicode(self))

    def __repr__(self):
        return '<Answer %d @ %x>' % (self.id, id(self))

class IDPartial(ComplexTransform):
    def __init__(self, model_type, fetch_callback):
        self.partial = PartialModelRef(model_type, fetch_callback)

    def __call__(self, key, value, model):
        return self.partial(key, {'id': value}, model)

class Question(JSONModel):
    """Describes a question on a StackExchange site."""
    transfer = ('tags', 'favorite_count', 'up_vote_count', 'down_vote_count',
        'view_count', 'score', 'community_owned', 'title', 'body',
        'body_markdown', 'is_answered', 'link', 'answer_count', 'can_close',
        'can_flag', 'close_vote_count', 'closed_reason', 'comment_count',
        'community_owned_date', 'delete_vote_count', 'down_vote_count',
        'downvoted', 'favorite_count', 'favorited', 'is_answered', 
        'accepted_answer_id', 'question_id', 'bounty_amount', 'upvoted',
        'reopen_vote_count', 'share_link', 'up_vote_count',
        ('creation_date', UNIXTimestamp),
        ('closed_date', UNIXTimestamp),
        ('last_edit_date', UNIXTimestamp),
        ('last_activity_date', UNIXTimestamp),
        ('bounty_closes_date', UNIXTimestamp),
        ('locked_date', UNIXTimestamp),
        ('protected_date', UNIXTimestamp),
        # XXX
        #('bounty_user', PartialModelRef(User, lambda s: s.site.user(s.id), extend = True)),
        #('last_editor', PartialModelRef(User, lambda s: s.site.user(s.id), extend = True)),
        ('timeline', LazySequenceField(TimelineEvent, 'questions/{id}/timeline')),
        ('revisions', LazySequenceField(PostRevision, 'posts/{id}/revisions')),
        ('comments', LazySequenceField(Comment, 'questions/{id}/comments', filter = '!-*7AsUyrEan0')),
        ('answers', ListOf(ModelRef(Answer))))
    alias = (('id', 'question_id'),
             ('accepted_answer', 'accepted_answer_id', IDPartial(Answer, lambda a: a.site.answer(a.id))))

    def _extend(self, json, site):
        if hasattr(json, 'owner') and 'user_id' in json.owner:
            self.owner_id = json.owner['user_id']

            owner_dict = dict(json.owner)
            owner_dict['id'] = self.owner_id
            del owner_dict['user_id']
            owner_dict['user_type'] = UserType.from_string(owner_dict['user_type'])

            self.owner = User.partial(lambda self: self.site.user(self.id), site, owner_dict)

        self.url = 'http://' + self.site.root_domain + '/questions/' + str(self.id)

    def fetch_callback(self, _):
        return self.site.question(self.id)

    def linked(self):
        return self.site.questions(linked_to = self.id)

    def related(self):
        return self.site.questions(related_to = self.id)

    def __repr__(self):
        return "<Question '%s' @ %x>" % (self.title, id(self))

##### Tags #####
class TagSynonym(JSONModel):
    transfer = ('from_tag', 'to_tag', 'applied_count',
        ('creation_date', UNIXTimestamp),
        ('last_applied_date', UNIXTimestamp))

    def __repr__(self):
        return "<TagSynonym '%s'->'%s'>" % (self.from_tag, self.to_tag)

class TagWiki(JSONModel):
    transfer = ('tag_name', 'body', 'excerpt',
        ('body_last_edit_date', UNIXTimestamp),
        ('excerpt_last_edit_date', UNIXTimestamp))

    def _extend(self, json, site):
        if hasattr(json, 'last_body_editor'):
            body_editor = dict(json.last_body_editor)
            body_editor['id'] = body_editor['user_id']
            del body_editor['user_id']
            self.last_body_editor = User.partial(lambda s: s.site.user(self.id), site, body_editor)

        if hasattr(json, 'last_excerpt_editor'):
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

class RepChange(JSONModel):
    """Describes an event which causes a change in reputation."""
    transfer = ('user_id', 'post_id', 'post_type', 'title', 'positive_rep',
        'negative_rep', ('on_date', UNIXTimestamp))

    def _extend(self, json, site):
        if hasattr(json, 'positive_rep') and hasattr(json, 'negative_rep'):
            self.score = json.positive_rep - json.negative_rep

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
    transfer = ('display_name', 'profile_image', 'age', 'website_url',
        'location', 'about_me', 'view_count', 'up_vote_count',
        'down_vote_count', 'account_id', 'profile_image', 'is_employee',
        ('creation_date', UNIXTimestamp),
        ('last_access_date', UNIXTimestamp),
        ('reputation', FormattedReputation),
        ('favorites', LazySequenceField(Question, 'users/{id}/favorites', response_key = 'questions')),
        ('no_answers_questions', LazySequenceField(Question, 'users/{id}/questions/no-answers', response_key = 'questions')),
        ('unanswered_questions', LazySequenceField(Question, 'users/{id}/questions/unanswered', response_key = 'questions')),
        ('unaccepted_questions', LazySequenceField(Question, 'users/{id}/questions/unaccepted', response_key = 'questions')),
        ('tags', LazySequenceField(Tag, 'users/{id}/tags')),
        ('badges', LazySequenceField(LaterClass('Badge'), 'users/{id}/badges')),
        ('timeline', LazySequenceField(TimelineEvent, 'users/{id}/timeline', response_key = 'user_timelines')),
        ('reputation_detail', LazySequenceField(RepChange, 'users/{id}/reputation')),
        ('mentioned', LazySequenceField(Comment, 'users/{id}/mentioned', response_key = 'comments')),
        ('comments', LazySequenceField(Comment, 'users/{id}/comments')),
        ('top_answer_tags', LazySequenceField(TopTag, 'users/{id}/top-answer-tags', response_key = 'top_tags')),
        ('top_question_tags', LazySequenceField(TopTag, 'users/{id}/top-question-tags', response_key = 'top_tags')),
        )

    # for compatibility reasons; association_id changed in v2.x
    alias = (('id', 'user_id'), ('association_id', 'account_id'),
             ('type', 'user_type', UserType.from_string))
    badge_types = ('gold', 'silver', 'bronze')

    def _extend(self, json, site):
        user_questions_url = 'users/%d/questions' % self.id
        question_count = getattr(json, 'question_count', None)
        self.questions = StackExchangeLazySequence(Question, question_count, site, user_questions_url, self._up('questions'))

        user_answers_url = 'users/%d/answers' % self.id
        answer_count = getattr(json, 'answer_count', None)
        self.answers = StackExchangeLazySequence(Answer, answer_count, site, user_answers_url, self._up('answers'))

        if hasattr(self, 'up_vote_count') and hasattr(self, 'down_vote_count'):
            self.vote_counts = (self.up_vote_count, self.down_vote_count)

        if hasattr(json, 'badge_counts'):
            self.badge_counts_t = tuple(json.badge_counts.get(c, 0) for c in ('gold', 'silver', 'bronze'))
            self.gold_badges, self.silver_badges, self.bronze_badges = self.badge_counts_t
            self.badge_counts = {
                BadgeType.Gold:   self.gold_badges,
                BadgeType.Silver: self.silver_badges,
                BadgeType.Bronze: self.bronze_badges
            }
            self.badge_total = sum(self.badge_counts_t)

        if hasattr(self, 'type'):
            self.is_moderator = self.type == UserType.Moderator

        self.url = 'http://' + self.site.root_domain + '/users/' + str(self.id)

    def has_privilege(self, privilege):
        return self.reputation >= privilege.reputation

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

class BadgeType(Enumeration):
    """Describes the rank or type of a badge: one of Bronze, Silver or Gold."""
    Bronze, Silver, Gold = range(3)

class Badge(JSONModel):
    """Describes a badge awardable on a StackExchange site."""
    transfer = ('name', 'description', 'award_count', 'tag_based',
                ('user', PartialModelRef(User, lambda s: s.site.user(s.id), extend = True)))
    alias = (('id', 'badge_id'),)

    @property
    def recipients(self):
        for badge in self.site.badge_recipients([self.id]):
            yield badge.user

    def __str__(self):
        return self.name
    def __repr__(self):
        return '<Badge \'%s\' @ %x>' % (self.name, id(self))

class Privilege(JSONModel):
    transfer = ('short_description', 'description', 'reputation')


class QuestionsQuery(object):
    def __init__(self, site):
        self.site = site

    def __call__(self, ids = None, user_id = None, **kw):
        self.site.check_filter(kw)

        # Compatibility hack, as user_id= was in versions below v1.1
        if ids is None and user_id is not None:
            return self.by_user(user_id, **kw)
        elif ids is None and user_id is None:
            return self.site.build('questions', Question, 'questions', kw)
        else:
            return self.site._get(Question, ids, 'questions', kw)

    def linked_to(self, qn, **kw):
        self.site.check_filter(kw)
        url = 'questions/%s/linked' % self.site.vectorise(qn, Question)
        return self.site.build(url, Question, 'questions', kw)

    def related_to(self, qn, **kw):
        self.site.check_filter(kw)
        url = 'questions/%s/related' % self.site.vectorise(qn, Question)
        return self.site.build(url, Question, 'questions', kw)

    def by_user(self, usr, **kw):
        self.site.check_filter(kw)
        kw['user_id'] = usr
        return self.site._user_prop('questions', Question, 'questions', kw)

    def unanswered(self, by = None, **kw):
        self.site.check_filter(kw)

        if by is None:
            return self.site.build('questions/unanswered', Question, 'questions', kw)
        else:
            kw['user_id'] = by
            return self.site._user_prop('questions/unanswered', Question, 'questions', kw)

    def no_answers(self, by = None, **kw):
        self.site.check_filter(kw)

        if by is None:
            return self.site.build('questions/no-answers', Question, 'questions', kw)
        else:
            kw['user_id'] = by
            return self.site._user_prop('questions/no-answers', Question, 'questions', kw)

    def unaccepted(self, by, **kw):
        self.site.check_filter(kw)
        kw['user_id'] = by
        return self.site._user_prop('questions/unaccepted', Questions, 'questions', kw)

    def favorited_by(self, by, **kw):
        self.site.check_filter(kw)
        kw['user_id'] = by
        return self.site._user_prop('favorites', Question, 'questions', kw)

