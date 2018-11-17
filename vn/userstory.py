import json
from vn.statistics import UserStoryStatistics
from vn.utility import remove_punct


class UserStory(object):
    def __init__(self, nr, text, no_punct):
        self.number = nr
        self.text = text
        self.sentence = no_punct
        self.iloc = []
        self.role = Role()
        self.means = Means()
        self.ends = Ends()
        self.indicators = []
        self.free_form = []
        self.system = WithMain()
        self.has_ends = False
        self.stats = UserStoryStatistics()

    def toJSON(self):
        if self.has_ends:
            {"number": self.number, "text": self.text, "iloc": self.iloc, "role": self.role.toJSON(),
             "means": self.means.toJSON(), "ends": self.ends.toJSON()}
        return {"number": self.number, "text": self.text, "iloc": self.iloc, "role": self.role.toJSON(),
                "means": self.means.toJSON()}

    def txtnr(self):
        return "US" + str(self.number)

    def is_func_role(self, token):
        if token.i in self.iloc:
            return True
        return False

    @staticmethod
    def parse(text, id, system_name, nlp, miner):
        """
        Create a new user story object and mines it to map all data in the user story text to a predefined model
        :param text: The user story text
        :param id: The user story ID, which can later be used to identify the user story
        :param system_name: Name of the system this user story belongs to
        :param nlp: Natural Language Processor (spaCy)
        :param miner: instance of class Miner
        :returns: UserStory
        """
        no_punct = remove_punct(text)
        no_double_space = ' '.join(no_punct.split())

        doc = nlp(no_double_space)

        user_story = UserStory(id, text, no_double_space)
        user_story.system.main = nlp(system_name)[0]
        user_story.data = doc

        miner.structure(user_story)
        user_story.old_data = user_story.data
        user_story.data = nlp(user_story.sentence)
        miner.mine(user_story, nlp)
        return user_story


class UserStoryPart(object):
    def __init__(self):
        self.text = []
        self.indicator = []
        self.indicator_t = ""
        self.indicator_i = -1
        self.simplified = ""

    def toJSON(self):
        return {"text": str(self.text), "indicator": str(self.indicator)}


class FreeFormUSPart(UserStoryPart):
    def __init__(self):
        super().__init__()
        self.simplified = ""
        self.main_verb = WithPhrase()
        self.main_object = WithPhrase()
        self.free_form = []
        self.verbs = []
        self.phrasal_verbs = []
        self.nouns = []
        self.proper_nouns = []
        self.noun_phrases = []
        self.compounds = []
        self.subject = WithPhrase()


class Role(UserStoryPart):
    def __init__(self):
        super().__init__()
        self.functional_role = WithPhrase()


class Means(FreeFormUSPart):
    pass


class Ends(FreeFormUSPart):
    pass


class WithMain(object):
    def __init__(self):
        self.main = []


class WithPhrase(WithMain):
    def __init__(self):
        super().__init__()
        self.phrase = []
        self.compound = []
        self.type = ""
