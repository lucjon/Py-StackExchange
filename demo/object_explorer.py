#!/usr/bin/env python
from __future__ import print_function

# a hack so you can run it 'python demo/object_explorer.py'
import sys
sys.path.append('.')
sys.path.append('..')
from stackauth import StackAuth
from stackexchange import Site, StackOverflow, StackExchangeLazySequence

try:
    get_input = raw_input
except NameError:
    get_input = input
    

site = None

print('Loading sites...',)
sys.stdout.flush()
all_sites = StackAuth().sites()
chosen_site_before = False
code_so_far = []

user_api_key = get_input("Please enter an API key if you have one (Return for none):")

def choose_site():
    global chosen_site_before

    print('\r                \rSelect a site (0 exits):')
    
    i = 1
    for site in all_sites:
        print('%d) %s' % (i, site.name))
        i += 1
    
    if i == 0:
        return
    else:
        site_def = all_sites[int(get_input('\nSite ID: ')) - 1]
    
    site = site_def.get_site()
    site.app_key = user_api_key or '1_9Gj-egW0q_k1JaweDG8Q'
    site.impose_throttling = True
    site.be_inclusive = True

    if not chosen_site_before:
        print('Use function names you would when using the Site, etc. objects.')
        print('return:    Move back up an object.')
        print('exit:    Quits.')
        print('dir:        Shows meaningful methods and properties on the current object.')
        print('dir*:    Same as dir, but includes *all* methods and properties.')
        print('code:    Show the code you\'d need to get to where you are now.')
        print('! before a non-function means "explore anyway."')
        print('a prompt ending in []> means the current item is a list.')

        chosen_site_before = True
    return (site, site_def)

def explore(ob, nm, pname=None):
    global code_so_far

    # sometimes, we have to use a different name for variables
    vname = nm if pname is None else pname

    is_dict = isinstance(ob, dict)
    is_list = isinstance(ob, list) or isinstance(ob, tuple) or is_dict
    suffix = '{}' if is_dict else '[]' if is_list else ''

    while True:
        # kind of hackish, but oh, well!
        inp = get_input('%s%s> ' % (nm, suffix))
        punt_to_default = False

        if inp == 'exit':
            sys.exit(0)
        elif inp == 'return':
            code_so_far = code_so_far[:-1]
            return
        elif inp == 'dir':
            if is_list:
                i = 0
                for item in ob:
                    print('%d) %s' % (i, str(item)))
                    i += 1
            else:
                print(repr([x for x in dir(ob) if not x.startswith('_') and x[0].lower() == x[0]]))
        elif inp == 'dir*':
            print(repr(dir(ob)))
        elif inp == 'code':
            print('\n'.join(code_so_far))
        elif is_list:
            try:
                item = ob[inp if is_dict else int(inp)]
                code_so_far.append('%s_item = %s[%s]' % (vname, vname, inp))
                explore(item, vname + '_item')
            except:
                print('Not in list... continuing as if was an attribute.')
                punt_to_default = True
        elif hasattr(ob, inp) or (len(inp) > 0 and inp[0] == '!') or punt_to_default:
            should_explore = False
            if inp[0] == '!':
                inp = inp[1:]
                should_explore = True

            rval = getattr(ob, inp)
            extra_code = ''

            if hasattr(rval, 'func_code'):
                # it's a function!

                if inp != 'fetch':
                    should_explore = True
                
                # we ask the user for each parameter in turn. we offset by one for self, after using reflection to find the parameter names.
                args = []
                for i in range(rval.func_code.co_argcount - 1):
                    name = rval.func_code.co_varnames[i + 1]
                    value = get_input(name + ': ')

                    if value == '':
                        value = None
                    else:
                        value = eval(value)

                    args.append(value)

                if len(args) > 0:
                    extra_code = '('
                    for arg in args:
                        extra_code += repr(arg) + ', '
                    extra_code = '%s)' % extra_code[:-2]
                else:
                    extra_code = '()'
                
                rval = rval(*args)

            if isinstance(rval, StackExchangeLazySequence):
                print('Fetching data...',)
                sys.stdout.flush()
                rval = rval.fetch()
                print('\r                 \rFetched. You\'ll need to remember to call .fetch() in your code.')
                
                extra_code = '.fetch()'
                should_explore = True
            
            if isinstance(rval, list) or isinstance(rval, tuple):
                should_explore = True

            print(repr(rval))
            if should_explore:
                # generate code
                code = '%s = %s.%s%s' % (inp, vname, inp, extra_code)
                code_so_far.append(code)

                explore(rval, inp)
        else:
            print('Invalid response.')

code_so_far.append('import stackexchange')
while True:
    site, site_def = choose_site()
    code_so_far.append('site = stackexchange.Site("' + site_def.api_endpoint[7:] + '")')
    explore(site, site_def.name, 'site')
