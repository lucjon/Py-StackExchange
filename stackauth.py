# stackauth.py - Implements basic StackAuth support for Py-StackExchange

from stackexchange.web import WebRequestManager
from stackexchange.core import *
from stackexchange import Site, User, UserType, SiteState, SiteType, MarkdownExtensions, SiteDefinition
import datetime, re

class Area51(object):
    def __getattr__(self, attr):
        raise Exception("You have encountered, through StackAuth association, Area51. Area51 is not accessible through the API.")

class UserAssociationSiteListing(JSONModel):
    transfer = ()

    def _extend(self, json, stackauth):
        self.name = json.site_name
        self.api_endpoint = json.site_url
        self.site_url = json.site_url

class UserAssociation(JSONModel):
    transfer = ('display_name', 'reputation', 'email_hash')
    has_endpoint = True
    
    def _extend(self, json, stackauth):
        self.id = json.user_id
        self.user_type = UserType.from_string(json.user_type)

        if not hasattr(json, 'site_url'):
            # assume it's Area 51 if we can't get a site out of it
            self.on_site = Area51()
            self.has_endpoint = False
        else:
            self.on_site = UserAssociationSiteListing(self.json, stackauth)

    def get_user(self):
        return self.on_site.get_site().user(self.id)

class StackAuth(object):
    def __init__(self, domain='api.stackexchange.com'):
        # 2010-07-03: There's no reason to change this now, but you never know.
        # 2013-11-11: Proven right, in a way, by v2.x...
        self.domain = domain
        self.api_version = '2.1'
    
    # These methods are slightly more complex than they
    # could be so they retain rough compatibility with
    # their StackExchange counterparts for paginated sets

    def url(self, u):
        # We need to stick an API version in now for v2.x
        return self.domain + '/' + self.api_version + '/' + u

    def build(self, url, typ, collection, kw = {}):
        mgr = WebRequestManager()
        json, info = mgr.json_request(url, kw)

        return JSONMangler.json_to_resultset(self, json, typ, collection, (self, url, typ, collection, kw))
    
    def sites(self):
        """Returns information about all the StackExchange sites currently listed."""
        # For optimisation purposes, it is explicitly expected in the documentation to have higher
        # values for the page size for this method.
        return self.build(self.url('sites'), SiteDefinition, 'api_sites', {'pagesize': 120})
    
    def api_associated_from_assoc(self, assoc_id):
        return self.associated_from_assoc(assoc_id, only_valid=True)

    def associated_from_assoc(self, assoc_id, only_valid = False):
        """Returns, given a user's *association ID*, all their accounts on other StackExchange sites."""
        # In API v2.x, the user_type attribute is not included by default, so we
        # need a filter.
        accounts = self.build(self.url('users/%s/associated' % assoc_id), UserAssociation, 'associated_users', {'filter': '0lWhwQSz'})
        if only_valid:
            return tuple([acc for acc in accounts if acc.has_endpoint])
        else:
            return accounts
    
    def associated(self, site, user_id, **kw):
        """Returns, given a target site object and a user ID for that site, their associated accounts on other StackExchange sites."""
        user = site.user(user_id)
        if hasattr(user, 'account_id'):
            assoc = user.account_id
            return self.associated_from_assoc(assoc, **kw)
        else:
            return []
    
    def api_associated(self, site, uid):
        return self.associated(site, uid, only_valid=True)
    
