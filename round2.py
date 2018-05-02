# I want something which is useful, and interesting to use.
# It should be fun for myself to talk to it. Otherwise I shouldn't present it.
# No one wants to know why it works, only how to use it.
# It should be able to express my points of view.
#

import pymongo as _pymongo

db = _pymongo.MongoClient()['conversations']

# Features of DB:
# + because MongoDB: simple object recall / query. easy prototyping
# + an object is an object is an object. everything is modifiable
#
# DB system: MongoDB
# Tables: a single table. no definition, it holds everything.
#
#
# "I understood ___(rephrasing of what was said)"
# "You sold your own ranch? Wow."
# "That's a lot of siblings!"
# 	** response is built on previous facts and knowledge of what "lot" and "little" as words mean. we can infer things.
#
# QUESTION:
# 	"What would you like to tell yourself in three months?"
# 	"Would you like me to tell you that in three months?"
# 	"Can you explain why [representation of question]?"
# 	"Has anything I've said not made sense?"
# 	"What's a better way to say 'Previous statement or question'?"
# 	"What's another way I can say 'Previous statement or question'?"
#
# RESPONSE:
# 	"I don't think that 'S'"
#
# responses as well as questions can trigger the interviewer's response.
# when someone expresses misunderstanding, we work to understand why we misunderstand.
# stop lines of questioning after a while "do you want to talk about something else?"
# types of questions can have descriptions, all of which refer to that question.
# 	this knowledge is built into the same system as everything else.
# 	the attributes of the python objects are modified by the Mongo query, when the question loads
