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