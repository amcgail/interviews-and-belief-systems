import g, exc


class Person(g.Obj):
    def __init__(self, **user_kwargs):
        if 'name' in user_kwargs:
            user_kwargs['bound'] = True

        g.Obj.__init__(self, **user_kwargs)

    def __str__(self):
        return "%s" % str(self['name'])
    def __repr__(self):
        return "[Person:%s]" % str(self['name'])


class Number(g.Obj):
    def __init__(self, **user_kwargs):
        if 'value' in user_kwargs:
            user_kwargs['bound'] = True

            # numbers can be identified uniquely by their value
            user_kwargs['_loadFromAttr'] = True
        g.Obj.__init__(self, **user_kwargs)

    @classmethod
    def parse(cls, text):
        if text in cls.waysOfSaying:
            number = cls.waysOfSaying[text]
        else:
            try:
                number = int(text)
            except ValueError:
                raise exc.Misunderstanding

        return cls( value=number )

    def __repr__(self):
        if self['bound']:
            return "[Number:%s]" % str(self['value'])
        else:
            return "[Number:unbound]"
    def __str__(self):
        return str(self['value'])


class Date(g.Obj):
    pass

# if False:
#     class Color(g.Obj):
#         def __init__(self, **user_kwargs):
#             g.Obj.__init__(self, **user_kwargs)
#
#             if 'value' not in self._attr:
#                 self['value'] = None
#             else:
#                 self['value'] = user_kwargs['value']
#                 self['bound'] = True
#
#             #print("created Number",kwargs, self.bound, self['value'])
#
#         @classmethod
#         def parse(cls, text):
#             if text in colors:
#                 color = colors[text]
#             else:
#                 conf = acts.Confirm(stmt.IsColor(text))
#
#             return cls( value=color )
#
#         def __str__(self):
#             return "[Number:%s]" % str(self['value'])
#         __repr__ = __str__