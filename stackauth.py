# stackauth.py - Implements basic StackAuth support for Py-StackExchange

from stackweb import WebRequestManager
from stackcore import *
import re

class SiteState(Enumeration):
	"""Describes the state of a StackExchange site."""
	Normal, OpenBeta, ClosedBeta, LinkedMeta = range(4)

class SiteDefinition(JSONModel):
	"""Contains information about a StackExchange site, reported by StackAuth."""
	
	transfer = ('name', 'logo_url', 'api_endpoint', 'site_url', 'description', 'icon_url', 'aliases')

	def _extend(self, json, stackauth):
		fixed_state = re.sub(r'_([a-z])', lambda match: match.group(1).upper(), json.state)
		fixed_state = fixed_state[0].upper() + fixed_state[1:]

		self.state = SiteState.from_string(fixed_state)
		self.styling = DictObject(json.styling)
		

class StackAuth(object):
	def __init__(self, **kw):
		# There's no reason to change this now, but you
		# never know.
		self.domain = kw['domain'] if 'domain' in kw else 'stackauth.com'
		self.use_gzip = kw['gzip'] if 'gzip' in kw else True
	
	# These methods are slightly more complex than they
	# could be so they retain rough compatibility with
	# their StackExchange counterparts for paginated sets

	def url(self, u):
		return 'http://' + self.domain + '/' + u

	def build(self, url, typ, collection, kw={}):
		mgr = WebRequestManager(gzip=self.use_gzip)
		json, info = mgr.json_request(url, kw)

		return JSONMangler.json_to_resultset(self, json, typ, collection, (self, url, typ, collection, kw))
	
	def sites(self):
		return self.build(self.url('sites'), SiteDefinition, 'api_sites')
	
