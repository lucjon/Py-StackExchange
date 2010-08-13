# stackweb.py - Core classes for web-request stuff

import urllib2, httplib, datetime, operator, StringIO, gzip, time
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
	def __init__(self, **kw):
		# Whether to attempt to de-gzip response
		self.use_gzip = kw['gzip'] if 'gzip' in kw else True
		# Whether to monitor requests for overuse of the API
		self.impose_throttling = kw['throttle'] if 'throttle' in kw else False
		# Whether to throw an error (when True) if the limit is reached, or wait until another request
		# can be made (when False).
		self.throttle_stop = kw['throttle_stop'] if 'throttle_stop' in kw else True
	
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
		for k, v in params.iteritems():
			if not done:
				url += '?'
				done = True
			else: url += '&'

			url += '%s=%s' % (k, v)
		request = urllib2.Request(url)
		
		if self.use_gzip:
			request.add_header('Accept-encoding', 'gzip')
		req_open = urllib2.build_opener()
		conn = req_open.open(request)

		req_data = conn.read()

		if self.use_gzip:
			data_stream = StringIO.StringIO(req_data)
			gzip_stream = gzip.GzipFile(fileobj=data_stream)
			actual_data = gzip_stream.read()
		else:
			actual_data = req_data

		info = conn.info()
		conn.close()

		return WebRequest(actual_data, info)
	
	def json_request(self, to, params):
		req = self.request(to, params)
		return (json.loads(req.data), req.info)

