import numpy as np

import g, exc, stmt


class YN(g.SpeechAct):

    def __init__(self, *args, **user_kwargs):
        g.SpeechAct.__init__(self, *args, **user_kwargs)
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
                print( "Saying it a bit randomly..." )
                print( "%s" % np.random.choice( wos ) )
        else:
            print( "I have no other way of saying it, so... " )

        print( self.bestWayOfSaying(self) )

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
            raise exc.Misunderstanding()

        return cls(value=True)

    def __str__(self):
        return str(self['value'])
    def __repr__(self):
        return "[YN:%s]" % str(self['value'])


class Confirm(g.SpeechAct):
    expectsResponse = True
    def __init__(self, toConfirm):
        super(Confirm, self).__init__(toConfirm)
        self.toConfirm = toConfirm
        self.expectedResponse = YN
        self.meaningContainer = stmt.IsTrue(toConfirm.copy(), YN(bound=False))

    def say(self):
        return "Just to be sure, you're saying %s?" % self.toConfirm.say()


class Request(g.SpeechAct):
    expectsResponse = True

    def __init__(self, toRequest):
        super(Request, self).__init__(toRequest)

        self.toRequest = toRequest
        howTo = self.toRequest.__request__()
        self.formulation = howTo['formulation']
        self.expectedResponse = howTo['expectation']
        self.meaningContainer = howTo['meaning']

    def say(self):
        return self.formulation


class DontKnowHowToAsk(g.SpeechAct):
    def say(self):
        return "I don't know how to ask this..."


class GetOrderSiblings:
    def __init__(self):
        pass