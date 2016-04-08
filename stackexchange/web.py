# stackweb.py - Core classes for web-request stuff
from __future__ import print_function

from stackexchange.core import StackExchangeError
from six.moves import urllib
import datetime, operator, io, gzip, time
import datetime
try:
    import json
except ImportError:
    import simplejson as json

class TooManyRequestsError(Exception):
    def __str__(self):
        return "More than 30 requests have been made in the last five seconds."

class WebRequest(object):
    data = ''
    info = None

    def __init__(self, data, info):
        self.data = data
        self.info = info
    
    def __str__(self):
        return str(self.data)

class WebRequestManager(object):
    debug = False
    cache = {}

    def __init__(self, impose_throttling = False, throttle_stop = True, cache = True, cache_age = 1800, force_http = False):
        # Whether to monitor requests for overuse of the API
        self.impose_throttling = impose_throttling
        # Whether to throw an error (when True) if the limit is reached, or wait until another request
        # can be made (when False).
        self.throttle_stop = throttle_stop
        # Whether to use request caching.
        self.do_cache = cache
        # The time, in seconds, for which to cache a response
        self.cache_age = cache_age
        # The time at which we should resume making requests after receiving a 'backoff' for each method
        self.backoff_expires = {}
        # Force the use of HTTP instead of HTTPS
        self.force_http = force_http
    
    # When we last made a request
    window = datetime.datetime.now()
    # Number of requests since last throttle window
    num_requests = 0

    def debug_print(self, *p):
        if WebRequestManager.debug:
            print(' '.join([x if isinstance(x, str) else repr(x) for x in p]))
    
    def canon_method_name(self, url):
        # Take the URL relative to the domain, without initial / or parameters
        parsed = urllib.parse.urlparse(url)
        return '/'.join(parsed.path.split('/')[1:])

    def request(self, url, params):
        now = datetime.datetime.now()

        # Quote URL fields (mostly for 'c#'), but not : in http://
        components = url.split('/')
        url = components[0] + '/'  + ('/'.join(urllib.parse.quote(path) for path in components[1:]))

        # Then add in the appropriate protocol
        url = '%s://%s' % ('http' if self.force_http else 'https', url)

        done = False
        for k, v in params.items():
            if not done:
                url += '?'
                done = True
            else:
                url += '&'

            url += '%s=%s' % (k, urllib.parse.quote(str(v).encode('utf-8')))
        
        # Now we have the `proper` URL, we can check the cache
        if self.do_cache and url in self.cache:
            timestamp, data = self.cache[url]
            self.debug_print('C>', url, '@', timestamp)

            if (now - timestamp).seconds <= self.cache_age:
                self.debug_print('Hit>', url)
                return data

        # Before we do the actual request, are we going to be throttled?
        def halt(wait_time):
            if self.throttle_stop:
                raise TooManyRequestsError()
            else:
                # Wait the required time, plus a bit of extra padding time.
                time.sleep(wait_time + 0.1)

        if self.impose_throttling:
            # We need to check if we've been told to back off
            method = self.canon_method_name(url)
            backoff_time = self.backoff_expires.get(method, None)
            if backoff_time is not None and backoff_time >= now:
                self.debug_print('backoff: %s until %s' % (method, backoff_time))
                halt((now - backoff_time).seconds)

            if (now - WebRequestManager.window).seconds >= 5:
                WebRequestManager.window = now
                WebRequestManager.num_requests = 0
            WebRequestManager.num_requests += 1
            if WebRequestManager.num_requests > 30:
                halt(5 - (now - WebRequestManager.window).seconds)

        # We definitely do need to go out to the internet, so make the real request
        self.debug_print('R>', url)
        request = urllib.request.Request(url)
        
        request.add_header('Accept-encoding', 'gzip')
        req_open = urllib.request.build_opener()

        try:
            conn = req_open.open(request)
            info = conn.info()
            req_data = conn.read()
            error_code = 200
        except urllib.error.HTTPError as e:
            # we'll handle the error response later
            error_code = e.code
            # a hack (headers is an undocumented property), but there's no sensible way to get them
            info = getattr(e, 'headers', {})
            req_data = e.read()

        # Handle compressed responses.
        # (Stack Exchange's API sends its responses compressed but intermediary
        # proxies may send them to us decompressed.)
        if info.get('Content-Encoding') == 'gzip':
            data_stream = io.BytesIO(req_data)
            gzip_stream = gzip.GzipFile(fileobj = data_stream)

            actual_data = gzip_stream.read()
        else:
            actual_data = req_data

        # Check for errors
        if error_code != 200:
            try:
                error_ob = json.loads(actual_data.decode('utf8'))
            except:
                raise StackExchangeError()
            else:
                raise StackExchangeError(error_ob.get('error_id', StackExchangeError.UNKNOWN), error_ob.get('error_name'), error_ob.get('error_message'))

        conn.close()
        req_object = WebRequest(actual_data, info)

        # Let's store the response in the cache
        if self.do_cache:
            self.cache[url] = (now, req_object)
            self.debug_print('Store>', url)

        return req_object
    
    def json_request(self, to, params):
        req = self.request(to, params)
        parsed_result = json.loads(req.data.decode('utf8'))

        # In API v2.x we now need to respect the 'backoff' warning
        if 'backoff' in parsed_result:
            method = self.canon_method_name(to)
            self.backoff_expires[method] = datetime.datetime.now() + datetime.timedelta(seconds = parsed_result['backoff'])

        return (parsed_result, req.info)
