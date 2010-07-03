# stackweb.py - Core classes for web-request stuff

import urllib2, httplib, datetime, operator, StringIO, gzip
try:
	import json
except ImportError:
	import simplejson as json

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
		self.use_gzip = kw['gzip'] if 'gzip' in kw else True
	
	def request(self, url, params):
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

