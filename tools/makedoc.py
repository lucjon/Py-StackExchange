#!/usr/bin/env python
# Creates HTML documentation from api.yml

import yaml

class Function(object):
    def __init__(self, id, tree_ob):
        def use(key, v=None):
            if key in tree_ob:
                val = tree_ob[key]
                
                if isinstance(val, str):
                    val = val.replace('<', '&lt;').replace('>', '&gt;')

                setattr(self, key, val)
                return True
            else:
                if v is not None:
                    setattr(self, key, v)
                return False

        self.id = id

        use('description', '')
        use('se_route', self.description)

        if not use('unimplemented', False):
            use('function')
            use('returns')
            use('parameters')
            use('see')
            use('example')
    
    @property
    def prototype(self):
        if self.unimplemented:
            raise AttributeError('prototype')
        elif hasattr(self, 'see'):
            return self.see
        else:
            params = ''

            if hasattr(self, 'parameters'):
                params = ', '.join(self.parameters.keys())

            return '%s(%s)' % (self.function, params)

class HTMLDocGenerator(object):
    def __init__(self, file_ob):
        self.categories = []

        self.parse(file_ob)
    
    def parse(self, file_ob):
        self.tree = yaml.load(file_ob)

        unimplemented = 0
        total = 0
    
        for name, category in self.tree.items():
            if name.startswith('__'):
                continue

            current_category = []

            for funct_id, function in category.items():
                f = Function('%s.%s' % (name, funct_id), function)

                if f.unimplemented:
                    unimplemented += 1

                total += 1
                current_category.append(f)

            self.categories.append((name, current_category))
    
    def to_html(self):
        html = []

        html.append('<style type="text/css">%s</style>' %  self.tree.get('__style__', ''))

        for category, functions in self.categories:
            html.append('<h2>%s</h2>' % category.title())

            for funct in functions:
                html.append('<a name="%s"></a>' % funct.id)
                html.append('<h3>%s</h3>' % funct.se_route)
                html.append('<div class="api">')

                if hasattr(funct, 'see'):
                    html.append('<div class="see">see <a href="#%s">%s</a></div>' % (funct.see, funct.see))
                    html.append('</div>')
                    continue

                if not funct.unimplemented:
                    html.append('<div class="prototype">%s</div>' % funct.prototype)

                html.append('<div class="description">%s</div>' % funct.description)
                
                if funct.unimplemented:
                    html.append('<div class="unimplemented">Unimplemented.</div>')
                    html.append('</div>')
                    continue


                if hasattr(funct, 'returns'):
                    html.append('<div class="returns">Returns: <span>%s</span></div>' % funct.returns)

                if hasattr(funct, 'parameters'):
                    html.append('<h4>Parameters</h4>')
                    html.append('<div class="params">')

                    for key, desc in funct.parameters.items():
                        html.append('<div><span class="param_name">%s</span> <span class="param_desc">%s</span></div>' % (key, desc))

                    html.append('</div>')

                if hasattr(funct, 'example'):
                    html.append('<h4>Example</h4>')
                    html.append('<pre class="example">%s</pre>' % funct.example)

                html.append('</div>')

        return '\n'.join(html)

if __name__ == '__main__':
    in_handle = open('api.yml')
    out_handle = open('api.html', 'w')

    docgen = HTMLDocGenerator(in_handle)
    out_handle.write(docgen.to_html())

    in_handle.close()
    out_handle.close()
