import abc
import timeit
from libs.NLPLoader import NLPLoader


class ModelGeneration:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        start_nlp_time = timeit.default_timer()
        loader = NLPLoader('NLP Initializer', 'en')
        self.nlp_time = timeit.default_timer() - start_nlp_time
        self._nlp = loader.nlp_tool

    @abc.abstractmethod
    def gen_concept_model(self):
        raise NotImplementedError()

    @property
    def nlp(self):
        return self._nlp
