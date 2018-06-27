"""
NOTES

haskell + neo4j:
	https://neo4j.com/developer/haskell/
	https://neo4j.com/developer/graph-database/
	https://neo4j.com/download/
	https://neo4j.com/developer/cypher/
"""

import acts, obj, g, stmt


def askAboutBrother():
    you = obj.Person(name="Alec", bound=True)
    numbrothers = obj.Number(bound=False)
    req = acts.Request(stmt.NumBrothers(person=you, num=numbrothers))
    g.initiateAct(req)

while 1:
    askAboutBrother()