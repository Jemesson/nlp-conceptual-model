import spacy


class NLPLoader:
    """
        Loads NLP Library
    """
    def __init__(self, message, language):
        self.message = message
        self.language = language
        self.nlp = spacy.load(self.language)

    def __str__(self):
        return f'Message: {self.message} Language: {self.language}'

    @property
    def nlp_tool(self):
        return self.nlp