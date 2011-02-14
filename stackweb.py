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

	def __init__(self, impose_throttling=False, throttle_stop=True):
		# Whether to monitor requests for overuse of the API
		self.impose_throttling = impose_throttling
		# Whether to throw an error (when True) if the limit is reached, or wait until another request
		# can be made (when False).
		self.throttle_stop = throttle_stop
	
	window = None
	num_requests = 0
	def request(self, url, params):
		if self.impose_throttling:
			now = datetime.datetime.now()
			if (window - now).seconds >= 5:
				window = now
				num_requests = 0
			num_requests += 1
			if num_requests > 30:
				if self.throttle_stop:
					raise TooManyRequestsError()
				else:
					# Wait the required time, plus a bit of extra padding time.
					time.sleep(5 - (window - now).seconds + 0.1)

		done = False

		# Quote URL fields (mostly for 'c#'), but not : in http://
		components = url.split('/')
		url = components[0] + '/'  + ('/'.join(urllib.quote(path) for path in components[1:]))

		for k, v in params.iteritems():
			if not done:
				url += '?'
				done = True
			else: url += '&'

			url += '%s=%s' % (k, urllib.quote(v))

		if WebRequestManager.debug:
			print 'R>', url

		request = urllib2.Request(url)
		
		request.add_header('Accept-encoding', 'gzip')
		req_open = urllib2.build_opener()
		conn = req_open.open(request)

		req_data = conn.read()

		data_stream = StringIO.StringIO(req_data)
		gzip_stream = gzip.GzipFile(fileobj=data_stream)
		actual_data = gzip_stream.read()

		info = conn.info()
		conn.close()

		return WebRequest(actual_data, info)
	
	def json_request(self, to, params):
		req = self.request(to, params)
		return (json.loads(req.data), req.info)

