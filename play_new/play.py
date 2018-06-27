# Who are you?
# What do you mean by that?
# Like what do you do for example? I know you're a computer, but I'm not sure how you work.

db = _pymongo.MongoClient()['conversations']['statements']

class Object:
    def __init__(self, uniqueName=None):
        pass

class Human(Object):
    def __init__(self, uniqueName):
        Object.__init__(self, uniqueName)

class Relation(Object):
    pass

class Sentence(Object):
    def __init__(self, *args):
        Object.__init__(self)

        if not isinstance(args[0], Relation):
            raise Exception("First argument to Sentence must be a relation...")

# know( Sentence( Relation("hasName"), Human("Alec"), str("Alec") ) )

class Statement(Object):
    def __init__(self, text):
        self.text = text

class Person(Object):
    pass

class Statement(Object):


"SaysIsTrue: [If something is large, it's also big], [Alec]"
"True: [If something is large, it's also big]"
