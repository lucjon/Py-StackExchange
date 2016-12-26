Py-StackExchange is a simple Python binding to the API of the StackExchange network of sites.

**NOTE**: Py-StackExchange is not an official product of, and is not affiliated in any way, with Stack Overflow Internet Services, Inc. 

# Getting Started
You can get Py-StackExchange in two ways:

  1. Clone the Git repository from Github.  
     If feasible, this is the recommended approach - you'll always get the latest code with the newest features.

	 git clone git://github.com/lucjon/Py-StackExchange.git

	 You'll need to set up paths, etc. on your own though.

  2. Install from the Python Package Index (PyPI)  
     It's easier to install the library with the easy_install command, but be warned: while major bug fixes will be deployed as soon as possible to PyPI, you might need to wait a while for new features.

	 easy_install Py-StackExchange

# Using the Library

Fire up your Python interpreter and import the stackexchange module. Yay, you're done!

    import stackexchange

The primary class in the bindings is the Site class; it is used for querying information from specific sites in the network.

    so = stackexchange.Site(stackexchange.StackOverflow)

A number of site URLs come predefined; the list is rebuilt every so often. A new site's URL may not be defined, in this case, simply use a string in the form `'api.joelfanclub.stackexchange.com'`. Don't put in `http://` or anything like that.

Once you have your site object, you can start to get some data dumped (using Py3/print_function syntax):

    u = so.user(41981)
    print(u.reputation.format())
    print(u.answers.count, 'answers')

## API Keys
If you're planning to use the API in an application or web service, especially one which will be making a large number of requests, you'll want to sign up for an API key on [StackApps](http://stackapps.com).

The API is rate-limited. The default rate limit, if no key is provided, is 300 requests per day. With an API key, however, this is bumped up to 10,000! You can also then use StackApps to publicise your app.

To use an API key with the library. simply pass it in like so:

    so = stackexchange.Site(stackexchange.StackOverflow, 'my_api_key')

Be aware, though, that even with an API key, requests are limited to thirty per five seconds. By default, the library will return an error before even making an HTTP request if you'll go over this limit. Alternatively, you can configure it such that it will wait until it can make another request without returning an error. To enable this behaviour. set the `impose_throttling` property:

    so.impose_throttling = True
	so.throttle_stop = False

## Lazy Lists
Py-StackExchange tries to limit the number of HTTP requests it makes, to help you squeeze the most out of your allotment. To this end, accessing any property which would require another call to fulfil requires that this be made explicit.

	me = so.user(41981)
    qs = me.questions

This will not return all the required data. You should instead use:

    qs = me.questions.fetch()

With the fetch call, the list contains the appropriate data. Note that after this, `me.questions` will contain the data; you only need to call `fetch()` once.

### Navigating Lists
The API uses a page-based system for navigating large datasets. This means that a set number (usually 30 or 60) of elements are fetched initially, with more available on-demand:

    print(qs.pagesize)
	# processing
	# Get more
	qs = qs.extend_next()
	# We have more questions

The `extend_next()` function returns a list with the extra data appended, `fetch_next()` returns just the new data.

# Next Steps
Read, and run, the example code. The programs are simple and cover most of the basic usage of the API. Many of the examples also have wiki pages on the Github site.

If you encounter any problems at all, feel free to leave an answer on [StackApps](https://stackapps.com/questions/198/py-stackexchange-an-api-wrapper-for-python), or to e-mail me at `lucas @ lucasjones . co.uk`. Yay, vanity domains.
