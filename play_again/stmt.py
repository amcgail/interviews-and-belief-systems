import acts, obj, g, exc


class IsTrue(g.SpeechAct):
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
        if not self.bool['bound'] and isinstance(entity, acts.YN):
            self.bool = entity
        else:
            raise exc.FillError()


class NumSisters(g.SpeechAct):
    expectsResponse = True
    def __init__(self, person, integer):
        g.SpeechAct.__init__(self)


class NumBrothers(g.SpeechAct):
    expectsResponse = True
    def __init__(self, **kwargs):
        super(NumBrothers, self).__init__(**kwargs)

    def say(self):
        if not self['person']['bound'] or not self['num']['bound']:
            raise exc.TooVagueToState()

        name = str(self['person'])
        have = "has"
        number = str(self['num'])
        return "{name} {have} {number} brothers.".format(**locals())

    def fill(self, entity):
        #print(self.person.bound, self.num.bound, self.num['value'], self.person['name'])
        if not self['person']['bound'] and isinstance(entity, obj.Person):
            self['person'] = entity
        elif not self['num']['bound'] and isinstance(entity, obj.Number):
            self['num'] = entity
        else:
            raise exc.FillError()

    def __request__(self):
        if not self['person']['bound'] and not self['num']['bound']:
            raise exc.InvalidRequestException()

        if not self['num']['bound']:
            # I suppose this should be contextual.
            # I'll worry about that later.

            do = "does"
            name = str(self['person'])
            have = "have"
            return {
                "formulation": "How many brothers {do} {name} {have}?".format(**locals()),
                "expectation": obj.Number,
                "meaning": NumBrothers(person=self['person'], num=obj.Number(bound=False))
            }
        else:
            return {
                "formulation": "I have no idea how to ask this... Hmmm...",
                "expectation": None,
                "meaning": acts.DontKnowHowToAsk()
            }


class IUnderstand(g.SpeechAct):
    def __init__(self, what, *args, **kwargs):
        super(IUnderstand, self).__init__(what, *args, **kwargs)
        self.expectedResponse = None
        self.what = what

    def say(self):
        return "Gotcha. " + self.what.say()


class DontUnderstand(g.SpeechAct):
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

        understanding = self.originalAct.meaningContainer
        understanding.fill(resp)

        g.initiateAct(IUnderstand(understanding))

        s1 = self.originalResponse
        s2 = newResponse
        g.initiateAct(acts.Confirm(SameMeaning(s1=s1, s2=s2)))


class FavoriteColor(g.SpeechAct):
    expectsResponse = True
    def __init__(self, person, color):
        super(FavoriteColor, self).__init__(person, color)
        self.person = person
        self.color = color

    def say(self):
        if not self.person['bound'] or not self.color['bound']:
            raise exc.TooVagueToState()

        name = str(self.person)
        color = str(self.color)
        return "{name}'s favorite color is {color}.".format(**locals())

    def fill(self, entity):
        #print(self.person['bound'], self.num['bound'], self.num['value'], self.person['name'])
        if not self.person['bound'] and isinstance(entity, obj.Person):
            self.person = entity
        elif not self.color['bound'] and isinstance(entity, obj.Color):
            self.color = entity
        else:
            raise exc.FillError()

    def __request__(self):
        if not self.person['bound'] and not self.color['bound']:
            raise exc.InvalidRequestException()
        if self.color['bound']:
            # I suppose this should be contextual.
            # I'll worry about that later.

            do = "does"
            name = str(self.person)
            have = "have"
            return {
                "formulation": "What is {name}'s favorite color?".format(**locals()),
                "expectation": obj.Color,
                "meaning": FavoriteColor(self.person, obj.Color(bound=False))
            }


class FirstSibling:
    def __init__(self):
        pass


class DateDifferenceIs:
    def __init__(self, d1, d2, dateDiff):
        pass


class SameMeaning(g.SpeechAct):
    def __init__(self, **kwargs):
        super(SameMeaning, self).__init__(**kwargs)

        print("kwargs",kwargs)

        if 's1' not in kwargs or 's2' not in kwargs:
            raise Exception("you need to say what has the same meaning as what...")

    def say(self):
        return "'%s' has the same meaning as '%s'" % (self['s1'], self['s2'])