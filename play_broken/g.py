import abc

import pymongo as _pymongo
from bson import ObjectId
import numpy as np


# it's all one fucking table!
db = _pymongo.MongoClient()['conversations']['everything']


class Obj:
    __metaclass__ = abc.ABCMeta

    waysOfSaying = {}

    # _waysOfSaying = None
    # @property
    # def waysOfSaying(self):
    #     if self._waysOfSaying is None:
    #         self._waysOfSaying = ###########**************8 finish this thought
    #     return self._waysOfSaying

    @staticmethod
    def toJSON(what):
        # the most important part is contracting objects!

        def mkjs(js):
            if type(js) in [str,int,ObjectId,bool,float]:
                return js
            if isinstance(js, Obj):
                print("HERE")

                if '_id' not in js._attr:
                    # js.bind()
                    if False:
                        raise Exception("There's no way I can write this to JSON if everything isn't bound...", js._attr)

                return js['_id']
            if isinstance(js, dict):
                newjs = {}
                for k, v in js.items():
                    newjs[k] = mkjs(v)
                return newjs
            raise Exception("I don't know what to do with", type(js))

        return mkjs(what)

    def convertMeToJSON(self):
        return self.toJSON(self._attr)

    def fromJSON(self, js):
        # the most important part is expanding objects!
        def mkattr(js):
            if type(js) in [str,int,bool]:
                return js
            if isinstance(js, ObjectId):
                return Obj(_id=js)
            if isinstance(js, dict):
                newjs = {}
                for k, v in js.items():
                    newjs[k] = mkattr(v)
                return newjs
            raise Exception("I don't know what to do with", type(js))

        return mkattr(js)

    def __init__(self, **user_kwargs):
        import bson

        # DEFAULTS
        kwargs = {
            "bound": False,
            "_loadFromAttr": False
        }
        kwargs.update(user_kwargs)
        self._attr = kwargs
        # if the object is not bound, that's it! we don't keep track of it. it may be abstract, etc. IDK OK

        self.loaded = False

        if "_id" in self._attr:

            # fix ID if need be...

            _id = self._attr['_id']
            if type( _id ) == str:
                self['_id'] = ObjectId(_id)

        # just faux-bind everything
        else:
            self._attr['_id'] = np.random.rand()

        self._attr['_class'] = self.__class__.__name__

    def copy(self):
        return self.__class__(**self._attr)

    def makeSureLoaded(self):
        # and load the sucker
        if ("_id" in self._attr or self._attr['bound']) and not self.loaded:
            try:
                self.load()
            except exc.LoadFailedException:
                print("binding new object", self._attr)
                self.bind()

    def __getitem__(self, item):
        self.makeSureLoaded()

        return self._attr[item]

    # always update the database!
    def __setitem__(self, key, value):
        if '_id' in self._attr and False:
            print(value)
            print(self.toJSON(value))
            db.update(
                {"_id": self._attr['_id']},
                { key: self.toJSON(value) }
            )
        self._attr[key] = value

    def update(self, query):
        if '_id' in self._attr:
            db.update(
                {"_id": self._attr['_id']},
                self.toJSON(query)
            )

        self.reload()

    def bind(self):
        self.loaded = True
        self._attr['_id'] = db.insert( self.toJSON(self._attr) )

    def loadAttr(self, attr):
        for k, v in attr.items():
            if k == "_id":
                self._attr['_id'] = v
                continue

            self._attr[k] = self.fromJSON(attr)

    def load(self):
        self.loaded = True
        if self._attr['_loadFromAttr']:
            # uniquely determined by attributes...
            findAttr = db.find_one(self._attr)
            if findAttr is None:
                raise exc.LoadFailedException()

            self.loadAttr(findAttr)
            return

        if "_id" not in self._attr:
            raise exc.LoadFailedException()
        findAttr = db.find_one({"_id": self['_id']})
        if findAttr is None:
            raise exc.LoadFailedException()
        self.loadAttr(findAttr)

    def reload(self):
        self._attr = {}
        self.loadAttr(db.find_one({"_id": self['_id']}))

    def newWayOfSaying(self, way):
        # OMFG this might work. beautiful
        self.waysOfSaying[way] = self
        self.waysOfSaying[self] = way

    def getHash(self):
        if '_id' not in self._attr:
            raise Exception("Can't hash unbound object!")
        return self['_id']
        # python 3 magic
        return int.from_bytes(str(self['_id']).encode(), 'little')

    def __hash__(self):
        self.makeSureLoaded()
        return self.getHash()
    def __eq__(self, other):
        self.makeSureLoaded()
        other.makeSureLoaded()
        return self.getHash() == other.getHash()



class Statement(Obj):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        super(Statement, self).__init__(**kwargs)

        self._initkwargs = kwargs

    def copy(self):
        return self.__class__(**self._initkwargs)


class SpeechAct(Obj):
    __metaclass__ = abc.ABCMeta
    expectsResponse = False
    expectedResponse = None

    def __init__(self, *args, **kwargs):
        super(SpeechAct, self).__init__(**kwargs)

        # speechActs should always exist as objects.
        # if not '_id' in self._attr:
        #     self.bind()

    @abc.abstractmethod
    def say(self):
        return []

    def parseResponse(self, response):
        understanding = self.expectedResponse.parse(response)

    def __str__(self):
        return self.say()
    __repr__ = __str__



# THESE PACKAGES must BE IMPORTED HERE
import acts, obj, exc, stmt


class LexiconLoader(Obj):

    def load(self):
        self.waysOfSaying.update({
            obj.Number(bound=True, value=1): "1",
            obj.Number(bound=True, value=2): "2",
            obj.Number(bound=True, value=3): "3",
            acts.YN(value=True): "Yes",
            acts.YN(value=False): "No"
        })

        for k,v in self.waysOfSaying.items():
            self.waysOfSaying[v] = k


def initiateAct( act ):
    print(act.say())
    if act.expectsResponse:
        # note. for python3 this is just input

        listen = raw_input(">>")
        try:
            act.parseResponse(listen)
            #for a in newActs:
            #    initiateAct( a )
        except exc.Misunderstanding:
            initiateAct(stmt.DontUnderstand(act, listen))