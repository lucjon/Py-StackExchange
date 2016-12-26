# stackcore.py - JSONModel/Enumeration + other utility classes that don't really belong now that the API's multi-file
# This file is relatively safe to "import *"

import datetime
from math import floor
from six.moves import urllib

## JSONModel base class
class JSONModel(object):
    """The base class of all the objects which describe API objects directly - ie, those which take JSON objects as parameters to their constructor."""

    def __init__(self, json, site, skip_ext = False):
        self.json = json
        self.json_ob = DictObject(json)
        self.site = site

        # we have four ways of specifying a field:
        #   - ('a', 'b') in alias: .a = JSON.b
        #   - 'name' in transfer: .name = JSON.name
        #   - ('a', 'b', t) in alias: .a = t(JSON.b)
        #   - ('name', t) in transfer: .name = t(JSON.name)
        # we unify these all into one set of descriptions
        alias = self.alias if hasattr(self, 'alias') else ()
        transfer = self.transfer if hasattr(self, 'transfer') else ()
        fields = ([A + (None,) for A in alias if len(A) == 2] +
                  [(k, k, None) for k in transfer if isinstance(k, str)] +
                  [A for A in alias if len(A) == 3] + 
                  [(k[0],) + k for k in transfer if not isinstance(k, str)])

        for dest, key, transform in fields:
            if hasattr(self.json_ob, key):
                value = getattr(self.json_ob, key)

                if isinstance(transform, ComplexTransform):
                    value = transform(key, value, self)
                elif transform is not None:
                    value = transform(value)

                setattr(self, dest, value)
            elif isinstance(transform, ComplexTransform):
                value = transform.no_value(key, self)
                if value is not None:
                    setattr(self, dest, value)

        if hasattr(self, '_extend') and not skip_ext:
            self._extend(self.json_ob, site)

    def fetch(self):
        """Fetches all the data that the model can describe, not just the attributes which were specified in the original response."""
        if hasattr(self, 'fetch_callback'):
            res = self.fetch_callback(self)

            if isinstance(res, dict):
                self.__init__(res, self.site)
            elif hasattr(res, 'json'):
                self.__init__(res.json, self.site)
            else:
                raise ValueError('Supplied fetch callback did not return a usable value.')
        else:
            return False

    # Allows the easy creation of updateable, partial classes
    @classmethod
    def partial(cls, fetch_callback, site, populate):
        """Creates a partial description of the API object, with the proviso that the full set of data can be fetched later."""

        model = cls({}, site, True)

        for k, v in populate.items():
            setattr(model, k, v)

        model.fetch_callback = fetch_callback
        return model

    # for use with Lazy classes that need a callback to actually set the model property
    def _up(self, a):
        """Returns a function which can be used with the LazySequence class to actually update the results properties on the model with the
new fetched data."""

        def inner(m):
            setattr(self, a, m)
        return inner

def LaterClassIn(name, module):
    def constructor(*a, **kw):
        cls = getattr(module, name)
        return cls(*a, **kw)
    constructor.__name__ = name
    return constructor

# a convenience 'type constructor' for producing datetime's from UNIX timestamps
UNIXTimestamp = lambda n: datetime.datetime.fromtimestamp(n)

# Some transforms are more complicated and need access to the model object
# itself, including Sites, etc. This is a base class to indicate this to the
# constructor.
class ComplexTransform(object):
    def no_value(self, key, model):
        pass

class ListOf(ComplexTransform):
    def __init__(self, transform):
        self.transform = transform

    def no_value(self, key, model):
        return []

    def __call__(self, key, value, model):
        if isinstance(self.transform, ComplexTransform):
            return [self.transform(key, v, model) for v in value]
        else:
            return [self.transform(v) for v in value]

class ModelRef(ComplexTransform):
    '''A convenience for foreign model references that take a JSON value and a reference to the underlying site object.'''
    def __init__(self, model_type):
        self.model_type = model_type

    def __call__(self, key, value, model):
        return self.model_type(value, model.site)

class PartialModelRef(ComplexTransform):
    def __init__(self, model_type, callback, extend = False):
        self.model_type = model_type
        self.callback = callback
        self.extend = extend

    def __call__(self, key, value, model):
        if self.extend:
            value = self.model_type(value, model.site, True)
            value.fetch_callback = self.callback
            return value
        else:
            return self.model_type.partial(self.callback, model.site, value)

class LazySequenceField(ComplexTransform):
    def __init__(self, m_type, url_format, count = None, update_key = None, response_key = None, **kw):
        self.m_type = m_type
        self.url_format = url_format
        self.count = count
        self.update_key = update_key
        self.response_key = response_key
        self.kw = kw

    def no_value(self, key, model):
        model_id = getattr(model, 'id', getattr(model.json_ob, key + '_id', None))
        url = self.url_format.format(id = model_id)
        response_key = key if self.response_key is None else self.response_key
        update_key = key if self.update_key is None else self.update_key
        return StackExchangeLazySequence(self.m_type, self.count, model.site,
                                            url, model._up(update_key),
                                            response_key, **self.kw)

    def __call__(self, key, value, model):
        return self.no_value(key, model)

class Enumeration(object):
    """Provides a base class for enumeration classes. (Similar to 'enum' types in other languages.)"""

    @classmethod
    def from_string(cls, text, typ = None):
        'Returns the appropriate enumeration value for the given string, mapping underscored names to CamelCase, or the input string if a mapping could not be made.'
        if typ is not None:
            if hasattr(typ, '_map') and text in typ._map:
                return getattr(typ, typ._map[text])
            elif hasattr(typ, text[0].upper() + text[1:]):
                return getattr(typ, text[0].upper() + text[1:])
            elif '_' in text:
                real_name = ''.join(x.title() for x in text.split('_'))
                if hasattr(typ, real_name):
                    return getattr(typ, real_name)
                else:
                    return text
            else:
                return text
        else:
            return cls.from_string(text, cls)

class StackExchangeError(Exception):
    """A generic error thrown on a bad HTTP request during a StackExchange API request."""
    UNKNOWN = -1

    def __init__(self, code = UNKNOWN, name = None, message = None):
        self.code = code
        self.name = name
        self.message = message
    
    def __str__(self):
        if self.code == self.UNKNOWN:
            return 'unrecognised error'
        else:
            return '%d [%s]: %s' % (self.code, self.name, self.message)

class EmptyResultset(tuple):
    def __new__(cls, json):
        instance = tuple.__new__(cls, [])

        for key in ('page_size', 'page', 'has_more', 'total', 'quota_max', 'quota_remaining', 'type'):
            if key in json:
                setattr(instance, key, json[key])

        return instance

class StackExchangeResultset(tuple):
    """Defines an immutable, paginated resultset. This class can be used as a tuple, but provides extended metadata as well, including methods
to fetch the next page."""

    def __new__(cls, items, build_info, has_more = True, page = 1, pagesize = None):
        if pagesize is None:
            pagesize = len(items)

        instance = tuple.__new__(cls, items)
        instance.page, instance.pagesize, instance.build_info = page, pagesize, build_info
        instance.items = items
        instance.has_more = has_more

        return instance

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

        new_set = new_params[0].build(*new_params[1:])
        new_set.page = page
        return new_set

    def fetch_extended(self, page):
        """Returns a new resultset containing data from this resultset AND from the specified page."""
        next = self.fetch_page(page)
        extended = self + next

        # max(0, ...) is so a non-zero, positive result for page is always found
        return StackExchangeResultset(extended, self.build_info, next.has_more, page)

    def fetch_next(self):
        """Returns the resultset of the data in the next page."""
        return self.fetch_page(self.page + 1)

    def extend_next(self):
        """Returns a new resultset containing data from this resultset AND from the next page."""
        return self.fetch_extended(self.page + 1)

    def fetch(self):
        # Do nothing, but allow multiple fetch calls
        return self

    def __iter__(self):
        return self.next()

    def next(self):
        current = self
        while True:
            for obj in current.items:
                yield obj
            if not current.has_more:
                return

            try:
                current = current.fetch_next()
                if len(current) == 0:
                    return
            except urllib.error.HTTPError:
                return

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

    def __init__(self, m_type, count, site, url, fetch = None, collection = None, **kw):
        self.m_type = m_type
        self.count = count
        self.site = site
        self.url = url
        self.fetch_callback = fetch
        self.kw = kw
        self.collection = collection if collection != None else self._collection(url)

    def _collection(self, c):
        return c.split('/')[-1]

    def __len__(self):
        if self.count != None:
            return self.count
        else:
            raise NeedsAwokenError(repr(self))

    def __repr__(self):
        if self.count is None:
            return '<unfetched sequence: %s>' % self.m_type.__name__
        else:
            return list.__repr__(self)

    def fetch(self, **direct_kw):
        """Fetch, from the API, the data this sequence is meant to hold."""
        # If we have any default parameters, include them, but overwrite any
        # passed in here directly.
        kw = dict(self.kw)
        kw.update(direct_kw)

        res = self.site.build(self.url, self.m_type, self.collection, kw)
        if self.fetch_callback != None:
            self.fetch_callback(res)
        return res

class StackExchangeLazyObject(list):
    """Provides a proxy to fetching a single item from a collection, lazily."""

    def __init__(self, m_type, site, url, fetch = None, collection = None):
        self.m_type = m_type
        self.site = site
        self.url = url
        self.fetch_callback = fetch
        self.collection = collection if collection != None else self._collection(url)

    def fetch(self, **kw):
        """Fetch, from the API, the data supposed to be held."""
        res = self.site.build(self.url, self.m_type, self.collection, kw)[0]
        if self.fetch_callback != None:
            self.fetch_callback(res)
        return res

    def __getattr__(self, key):
        raise NeedsAwokenError

#### Hack, because I can't be bothered to fix my mistaking JSON's output for an object not a dict
# (Si jeunesse savait, si vieillesse pouvait...)
# Attrib: Eli Bendersky, http://stackoverflow.com/questions/1305532/convert-python-dict-to-object/1305663#1305663
class DictObject:
    def __init__(self, entries):
        self.__dict__.update(entries)

class JSONMangler(object):
    """This class handles all sorts of random JSON-handling stuff"""

    @staticmethod
    def paginated_to_resultset(site, json, typ, collection, params):
        # N.B.: We ignore the 'collection' parameter for now, given that it is
        # no longer variable in v2.x, having been replaced by a generic field
        # 'items'. To perhaps be removed completely at some later point.
        items = []
        
        # create strongly-typed objects from the JSON items
        for json_item in json['items']:
            json_item['_params_'] = params[-1] # convenient access to the kw hash
            items.append(typ(json_item, site))

        rs = StackExchangeResultset(items, params, json['has_more'])
        if 'total' in json:
            rs.total = json['total']

        return rs

    @staticmethod
    def normal_to_resultset(site, json, typ, collection):
        # the parameter 'collection' may be need in future, and was needed pre-2.0
        return tuple([typ(x, site) for x in json['items']])

    @classmethod
    def json_to_resultset(cls, site, json, typ, collection, params = None):
        # this is somewhat of a special case, introduced by some filters in
        # post-2.0 allowing only 'metadata' to be returned
        if 'items' not in json:
            return EmptyResultset(json)
        elif 'has_more' in json:
            # we have a paginated resultset
            return cls.paginated_to_resultset(site, json, typ, collection, params)
        else:
            # this isn't paginated (unlikely but possible - eg badges)
            return cls.normal_to_resultset(site, json, typ, collection)

def format_relative_date(date, relative_to = None):
    """Takes a datetime object and returns the date formatted as a string e.g. "3 minutes ago", like the real site, relative to the given datetime. If no datetime is given, default to the current time."""
    # This is based roughly on George Edison's code from StackApps:
    #   http://stackapps.com/questions/1009/how-to-format-time-since-xxx-e-g-4-minutes-ago-similar-to-stack-exchange-site/1018#1018"""

    now = datetime.datetime.now() if relative_to is None else relative_to
    diff = (now - date).seconds

    # Anti-repetition! These simplify the code somewhat.
    plural = lambda d: 's' if d != 1 else ''
    frmt   = lambda d: (diff / float(d), plural(diff / float(d)))

    if diff < 60:
        return '%d second%s ago' % frmt(1)
    elif diff < 3600:
        return '%d minute%s ago' % frmt(60)
    elif diff < 86400:
        return '%d hour%s ago' % frmt(3600)
    elif diff < 172800:
        return 'yesterday'
    else:
        return date.strftime('M j / y - H:i')

class Sort(Enumeration):
    Activity = 'activity'
    Views = 'views'
    Creation = 'creation'
    Votes = 'votes'

ASC = 'asc'
DESC = 'desc'
