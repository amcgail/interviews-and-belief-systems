"""
NOTES

haskell + neo4j:
	https://neo4j.com/developer/haskell/
	https://neo4j.com/developer/graph-database/
	https://neo4j.com/download/
	https://neo4j.com/developer/cypher/
"""
import abc
import pymongo as _pymongo
from bson import ObjectId
import numpy as np

# it's all one fucking table!
db = _pymongo.MongoClient()['conversations']['everything']


class LoadFailedException(Exception):
    pass
class InvalidRequestException(Exception):
    pass
class Misunderstanding(Exception):
    pass
class FillError(Exception):
    pass
class TooVagueToState(Exception):
    pass

class Obj:
    __metaclass__ = abc.ABCMeta

    waysOfSaying = {}

    # _waysOfSaying = None
    # @property
    # def waysOfSaying(self):
    #     if self._waysOfSaying is None:
    #         self._waysOfSaying = ###########**************8 finish this thought
    #     return self._waysOfSaying

    def toJSON(self):
        return self._attr

    def __init__(self, **user_kwargs):
        # DEFAULTS
        kwargs = {
            "bound": False
        }
        kwargs.update(user_kwargs)
        self._attr = kwargs
        # if the object is not bound, that's it! we don't keep track of it. it may be abstract, etc. IDK OK

        # fix ID if need be...
        if "_id" in self._attr:
            _id = self._attr['_id']
            if type( self._attr['_id'] ) == str:
                self['_id'] = ObjectId(_id)

        # For bound objects, we should load the properties, or something!
        if not self['bound']:
            #something
            pass
        else:
            try:
                self.load()
            except LoadFailedException:
                print(self._attr)
                self.bind()

    def copy(self):
        return Obj(_id=self['_id'])

    def __getitem__(self, item):
        return self._attr[item]

    # always update the database!
    def __setitem__(self, key, value):
        if '_id' in self._attr:
            db.update(
                {"_id": self._attr['_id']},
                { key: value }
            )
        self._attr[key] = value

    def update(self, query):
        if '_id' in self._attr:
            db.update(
                {"_id": self._attr['_id']},
                query
            )

        self.reload()

    def bind(self):
        self._attr['_id'] = db.insert(self._attr)

    def load(self):
        self._attr = db.find_one(self._attr)
        if self._attr is None:
            raise LoadFailedException()

    def reload(self):
        self._attr = db.find_one({"_id": self['_id']})

    def newWayOfSaying(self, way):
        # OMFG this might work. beautiful
        self.waysOfSaying[way] = self
        self.waysOfSaying[self] = way

    def __hash__(self):
        return self['_id']
    def __eq__(self, other):
        return self['_id'] == other['_id']

class Person(Obj):
    def __init__(self, *args, **user_kwargs):
        Obj.__init__(self, *args, **user_kwargs)
        kwargs = {
            "bound": False
        }
        kwargs.update(user_kwargs)

        self['name'] = None
        self.bound = kwargs['bound']

        if 'name' in kwargs:
            self['name'] = kwargs['name']
            self.bound = True

    def __str__(self):
        return "%s" % str(self['name'])
    def __repr__(self):
        return "[Person:%s]" % str(self['name'])


class Number(Obj):
    def __init__(self, *args, **user_kwargs):
        Obj.__init__(self, *args, **user_kwargs)
        kwargs = {
            "bound": False
        }
        kwargs.update(user_kwargs)

        self['value'] = None
        self.bound = kwargs['bound']

        if 'value' in kwargs:
            self['value'] = kwargs['value']
            self.bound = True

        #print("created Number",kwargs, self.bound, self['value'])

    @classmethod
    def parse(cls, text):
        if text in cls.waysOfSaying:
            number = cls.waysOfSaying[text]
        else:
            try:
                number = int(text)
            except ValueError:
                raise Misunderstanding

        return cls( value=number )

    def __repr__(self):
        return "[Number:%s]" % str(self['value'])
    def __str__(self):
        return str(self['value'])

class Date(Obj):
    pass

class Statement(Obj):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        super(Statement, self).__init__(**kwargs)

        self._initargs = args
        self._initkwargs = kwargs

    def copy(self):
        #print( self._initargs, self._initkwargs )
        return self.__class__(*self._initargs, **self._initkwargs)

class SpeechAct(Obj):
    __metaclass__ = abc.ABCMeta
    expectsResponse = False
    expectedResponse = None

    def __init__(self, *args, **kwargs):
        super(SpeechAct, self).__init__(**kwargs)
        self.bind()

    @abc.abstractmethod
    def say(self):
        return []

    def parseResponse(self, response):
        understanding = self.expectedResponse.parse(response)

    def __str__(self):
        return self.say()
    __repr__ = __str__

class YN(SpeechAct):

    def __init__(self, *args, **user_kwargs):
        SpeechAct.__init__(self, *args, **user_kwargs)
        kwargs = {
            "bound": False
        }
        kwargs.update(user_kwargs)

        self['value'] = None
        self.bound = kwargs['bound']

        if 'value' in kwargs:
            assert type( kwargs['value'] ) == bool

            self['value'] = kwargs['value']
            self.bound = True

    def say(self):
        # always think about saying it another random way you want...
        wos = self.waysOfSaying[ self ]
        if len(wos) > 0:
            if np.random.rand() > 0.8:
                print "Saying it a bit randomly..."
                print "%s" % np.random.choice( wos )
        else:
            print "I have no other way of saying it, so... "

        print self.bestWayOfSaying(self)

    def bestWayOfSaying(self):
        if self['value']:
            return "Yes"
        else:
            return "No"

    @classmethod
    def parse(cls, text):
        yn = None
        if text in cls.waysOfSaying:
            yn = cls.waysOfSaying[text]
        else:
            if text.lower() == "yes":
                # confirmed
                yn = True
            if text.lower() == "no":
                yn = False

        if yn is None:
            raise Misunderstanding()

        return cls(value=True)

    def __str__(self):
        return str(self['value'])
    def __repr__(self):
        return "[YN:%s]" % str(self['value'])

class SameMeaning(SpeechAct):
    def __init__(self, str1, str2):
        super(SameMeaning, self).__init__(str1, str2)

        self.str1 = str1
        self.str2 = str2

    def say(self):
        return "'%s' has the same meaning as '%s'" % (self.str1, self.str2)

class IsTrue(SpeechAct):
    def __init__(self, stmt, bool):
        super(IsTrue, self).__init__(stmt, bool)

        self.stmt = stmt
        self.bool = bool

    def say(self):
        stmt = self.stmt.say()
        if self.bool['value']:
            isnot = "is"
        else:
            isnot = "is not"
        return "\"{stmt}\" {isnot} true".format(**locals())

    def fill(self, entity):
        #print(self.person.bound, self.num.bound, self.num['value'], self.person['name'])
        if not self.bool['bound'] and isinstance(entity, YN):
            self.bool = entity
        else:
            raise FillError()

class Confirm(SpeechAct):
    expectsResponse = True
    def __init__(self, stmt):
        super(Confirm, self).__init__(stmt)
        self.stmt = stmt
        self.expectedResponse = YN
        self.meaningContainer = IsTrue( stmt.copy(), YN(bound=False) )

    def say(self):
        return "Just to be sure, you're saying %s?" % self.stmt.say()

class Request(SpeechAct):
    expectsResponse = True

    def __init__(self, stmt):
        super(Request, self).__init__(stmt)

        self.stmt = stmt
        howTo = self.stmt.__request__()
        self.formulation = howTo['formulation']
        self.expectedResponse = howTo['expectation']
        self.meaningContainer = howTo['meaning']

    def say(self):
        return self.formulation

class IUnderstand(SpeechAct):
    def __init__(self, what, *args, **kwargs):
        super(IUnderstand, self).__init__(what, *args, **kwargs)
        self.expectedResponse = None
        self.what = what

    def say(self):
        return "Gotcha. " + self.what.say()

class DontUnderstand(SpeechAct):
    expectsResponse = True

    def __init__(self, originalAct, originalResponse):
        super(DontUnderstand, self).__init__(originalAct, originalResponse)

        self.originalAct = originalAct
        self.originalResponse = originalResponse
        self.expectedResponse = self.originalAct.expectedResponse

    def say(self):
        return "I didn't quite understand that. Can you express that in another way?"

    def parseResponse(self, newResponse):
        # what we expected

        #print("originalAct:", self.originalAct.__class__)
        resp = self.expectedResponse.parse(newResponse)
        resp.newWayOfSaying(self.originalResponse)

        understanding = self.originalAct.meaningContainer.copy()
        understanding.fill(resp)

        initiateAct(IUnderstand(understanding))

        s1 = self.originalResponse
        s2 = newResponse
        initiateAct(Confirm(SameMeaning(s1, s2)))

class NumSisters(SpeechAct):
    expectsResponse = True
    def __init__(self, person, integer):
        SpeechAct.__init__(self)

class DontKnowHowToAsk(SpeechAct):
    def say(self):
        return "I don't know how to ask this..."

# this is "how do we say something" "how do we comprehend something"?
class NumBrothers(SpeechAct):
    expectsResponse = True
    def __init__(self, person, num):
        self.person = person
        self.num = num

        super(NumBrothers, self).__init__(person, num)

    def say(self):
        if not self.person['bound'] or not self.num['bound']:
            raise TooVagueToState()

        name = str(self.person)
        have = "has"
        number = str(self.num)
        return "{name} {have} {number} brothers.".format(**locals())

    def fill(self, entity):
        #print(self.person.bound, self.num.bound, self.num['value'], self.person['name'])
        if not self.person['bound'] and isinstance(entity, Person):
            self.person = entity
        elif not self.num['bound'] and isinstance(entity, Number):
            self.num = entity
        else:
            raise FillError()

    def __request__(self):
        if not self.person['bound'] and not self.num['bound']:
            raise InvalidRequestException()

        if not self.num['bound']:
            # I suppose this should be contextual.
            # I'll worry about that later.

            do = "does"
            name = str(self.person)
            have = "have"
            return {
                "formulation": "How many brothers {do} {name} {have}?".format(**locals()),
                "expectation": Number,
                "meaning": NumBrothers(self.person, Number(bound=False))
            }
        else:
            return {
                "formulation": "I have no idea how to ask this... Hmmm...",
                "expectation": None,
                "meaning": DontKnowHowToAsk()
            }

# I just kept going...
if False:
    colors = {}
    class Color(Obj):
        def __init__(self, **user_kwargs):
            Obj.__init__(self, **user_kwargs)

            if 'value' not in self._attr:
                self['value'] = None
            else:
                self['value'] = kwargs['value']
                self['bound'] = True

            #print("created Number",kwargs, self.bound, self['value'])

        @classmethod
        def parse(cls, text):
            if text in colors:
                color = colors[text]
            else:
                conf = Confirm(IsColor(text))

            return cls( value=color )

        def __str__(self):
            return "[Number:%s]" % str(self['value'])
        __repr__ = __str__


    class FavoriteColor(SpeechAct):
        expectsResponse = True
        def __init__(self, person, color):
            super(FavoriteColor, self).__init__(person, color)
            self.person = person
            self.color = color

        def say(self):
            if not self.person['bound'] or not self.color['bound']:
                raise TooVagueToState()

            name = str(self.person)
            color = str(self.color)
            return "{name}'s favorite color is {color}.".format(**locals())

        def fill(self, entity):
            #print(self.person['bound'], self.num['bound'], self.num['value'], self.person['name'])
            if not self.person['bound'] and isinstance(entity, Person):
                self.person = entity
            elif not self.color['bound'] and isinstance(entity, Color):
                self.color = entity
            else:
                raise FillError()

        def __request__(self):
            if not self.person['bound'] and not self.color['bound']:
                raise InvalidRequestException()
            if self.color['bound']:
                # I suppose this should be contextual.
                # I'll worry about that later.

                do = "does"
                name = str(self.person)
                have = "have"
                return {
                    "formulation": "What is {name}'s favorite color?".format(**locals()),
                    "expectation": Color,
                    "meaning": FavoriteColor(self.person, Color(bound=False))
                }

# larger directive. idk what to do with this yet
class GetOrderSiblings:
    def __init__(self):
        pass


class FirstSibling:
    def __init__(self):
        pass

class DateDifferenceIs:
    def __init__(self, d1, d2, dateDiff):
        pass

def initiateAct( act ):
    print(act.say())
    if act.expectsResponse:
        listen = raw_input(">>")
        try:
            act.parseResponse(listen)
            #for a in newActs:
            #    initiateAct( a )
        except Misunderstanding:
            initiateAct( DontUnderstand( act, listen ) )


class LexiconLoader(Obj):

    def load(self):
        self.waysOfSaying.update({
            Number(bound=True, value=1): "1",
            Number(bound=True, value=2): "2",
            Number(bound=True, value=3): "3",
            "1": Number(bound=True, value=1),
            "2": Number(bound=True, value=2),
            "3": Number(bound=True, value=3)
        })

if __name__ == '__main__':
    while 1:
        #print(waysOfSaying)
        you = Person(name="Alec", bound=True)
        numbrothers = Number(bound=False)
        req = Request(NumBrothers(you, numbrothers))
        initiateAct(req)