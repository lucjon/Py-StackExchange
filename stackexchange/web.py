# stackweb.py - Core classes for web-request stuff

import urllib2, httplib, datetime, operator, StringIO, gzip, time, urllib
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

	def __init__(self, impose_throttling=False, throttle_stop=True, cache=True, cache_age=1800):
		# Whether to monitor requests for overuse of the API
		self.impose_throttling = impose_throttling
		# Whether to throw an error (when True) if the limit is reached, or wait until another request
		# can be made (when False).
		self.throttle_stop = throttle_stop
		# Whether to use request caching.
		self.do_cache = cache
		# The time, in seconds, to cache a response
		self.cache_age = cache_age

	# When we last made a request
	window = datetime.datetime.now()
	# Number of requests since last throttle window
	num_requests = 0

	def debug_print(self, *p):
		if WebRequestManager.debug:
			print ' '.join([x if isinstance(x, str) else repr(x) for x in p])

	def request(self, url, params):
		now = datetime.datetime.now()

		# Quote URL fields (mostly for 'c#'), but not : in http://
		components = url.split('/')
		url = components[0] + '/'  + ('/'.join(urllib.quote(path) for path in components[1:]))

		done = False
		for k, v in params.iteritems():
			if not done:
				url += '?'
				done = True
			else: url += '&'

			url += '%s=%s' % (k, urllib.quote(v.encode('utf-8')))
		
		# Now we have the `proper` URL, we can check the cache
		if self.do_cache and url in self.cache:
			timestamp, data = self.cache[url]
			self.debug_print('C>', url, '@', timestamp)

			if (now - timestamp).seconds <= self.cache_age:
				self.debug_print('Hit>', url)
				return data

		# Before we do the actual request, are we going to be throttled?
		if self.impose_throttling:
			if (now - WebRequestManager.window).seconds >= 5:
				WebRequestManager.window = now
				WebRequestManager.num_requests = 0
			WebRequestManager.num_requests += 1
			if WebRequestManager.num_requests > 30:
				if self.throttle_stop:
					raise TooManyRequestsError()
				else:
					# Wait the required time, plus a bit of extra padding time.
					time.sleep(5 - (WebRequestManager.window - now).seconds + 0.1)

		# We definitely do need to go out to the internet, so make the real request
		self.debug_print('R>', url)
		request = urllib2.Request(url)

		request.add_header('Accept-encoding', 'gzip')
		req_open = urllib2.build_opener()
		conn = req_open.open(request)

		req_data = conn.read()

		# Handle compressed responses.
		# (Stack Exchange's API sends its responses compressed but intermediary
		# proxies may send them to us decompressed.)
		if conn.info().getheader('Content-Encoding') == 'gzip':
			data_stream = StringIO.StringIO(req_data)
			gzip_stream = gzip.GzipFile(fileobj=data_stream)

			actual_data = gzip_stream.read()
		else:
			actual_data = req_data

		info = conn.info()
		conn.close()

		req_object = WebRequest(actual_data, info)

		# Let's store the response in the cache
		if self.do_cache:
			self.cache[url] = (now, req_object)
			self.debug_print('Store>', url)

		return req_object
	
	def json_request(self, to, params):
		req = self.request(to, params)
		return (json.loads(req.data), req.info)

