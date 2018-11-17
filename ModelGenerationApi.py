import timeit

from ModelGeneration import ModelGeneration
from vn.miner import StoryMiner
from vn.statistics import Statistics, Counter
from vn.userstory import UserStory
from vn.matrix import Matrix
from vn.pattern import Constructor


class ModelGenerationApi(ModelGeneration):
    """
        Model generation from API (e.g: we can use postman to consume)
    """
    def __init__(self, system_name, threshold, base_weight, weights, messages):
        super().__init__()
        self.system_name = system_name
        self.threshold = threshold
        self.base_weight = base_weight
        self.weights = weights
        self.messages = messages
        self.link = False

    def gen_concept_model(self):
        nlp = self.nlp

        miner = StoryMiner()
        counter = Counter()

        # Keep tracking the number of successes and fails
        success = 0
        fail = 0

        # Keeps tracking of all success and failed User Stories
        user_stories_lst = []
        failed_stories_lst = []
        success_stories_lst = []

        us_id = 1

        # Parse every user story (remove punctuation and mine)
        for story_line in self.messages:
            try:
                user_story = UserStory.parse(story_line, us_id, self.system_name, nlp, miner)
                user_story = counter.count(user_story)
                success = success + 1
                user_stories_lst.append(user_story)
                success_stories_lst.append(story_line)
            except ValueError as err:
                failed_stories_lst.append([us_id, story_line, err.args])
                fail = fail + 1
            us_id = us_id + 1

        # Generate the term-by-user story matrix (m), and additional data in two other matrices
        matrix = Matrix(self.base_weight, self.weights)
        matrices = matrix.generate(user_stories_lst, ' '.join([u.sentence for u in user_stories_lst]), nlp)
        m, count_matrix, stories_list, rme = matrices

        # Generate the ontology

        patterns = Constructor(nlp, user_stories_lst, m)
        out = patterns.make(self.system_name, self.threshold, self.link)
        output_ontology, output_prolog, output_ontobj, output_prologobj, onto_per_role = out

        # Return objects so that they can be used as input for other tools
        return {'stories': user_stories_lst, 'ontology': output_ontology, 'prolog': output_prolog, 'matrix': m}


if __name__ == '__main__':
    weights = [1, 1, 1, 0.7, 0.5, 0.66]
    messages = [
        'As a Visitor, I want to choose a payment method so that I can buy a ticket.',
        'As a Visitor, I want to receive a purchased ticket.'
    ]

    conceptual_model = ModelGenerationApi('system-name', 1, 1, weights, messages)
    result = conceptual_model.gen_concept_model()

    print(result)