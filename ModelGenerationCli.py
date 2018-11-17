import timeit
import os.path
import pkg_resources

from ModelGeneration import ModelGeneration
from vn.miner import StoryMiner
from vn.io import Reader, Writer
from vn.statistics import Statistics, Counter
from vn.userstory import UserStory
from vn.utility import Printer, multiline
from vn.matrix import Matrix
from vn.pattern import Constructor
from vn.generator import Generator


class ModelGenerationFromCli(ModelGeneration):
    def __init__(self, args, weights):
        super().__init__()
        self.filename = args.filename
        self.system_name = args.system_name
        self.print_us = args.print_us
        self.print_ont = args.print_ont
        self.statistics = args.statistics
        self.link = args.link
        self.prolog = args.prolog
        self.json = args.json
        self.per_role = args.per_role
        self.threshold = args.threshold
        self.base_weight = args.base_weight
        self.weights = weights

    def gen_concept_model(self):
        nlp = self.nlp
        nlp_time = self.nlp_time

        start_parse_time = timeit.default_timer()
        miner = StoryMiner()

        # Read the input file
        story_lines = Reader.parse(self.filename)
        us_id = 1

        # Keep tracking the number of successes and fails
        success = 0
        fail = 0

        list_of_fails = []
        errors = ""
        counter = Counter()

        # Keeps tracking of all success and failed User Stories
        user_stories_lst = []
        failed_stories_lst = []
        success_stories_lst = []

        # Parse every user story (remove punctuation and mine)
        for story_line in story_lines:
            try:
                user_story = UserStory.parse(story_line, us_id, self.system_name, nlp, miner)
                user_story = counter.count(user_story)
                success = success + 1
                user_stories_lst.append(user_story)
                success_stories_lst.append(story_line)
            except ValueError as err:
                failed_stories_lst.append([us_id, story_line, err.args])
                errors += "\n[User Story " + str(us_id) + " ERROR] " + str(err.args[0]) + "! (\"" + " ".join(
                    str.split(story_line)) + "\")"
                fail = fail + 1
            us_id = us_id + 1

        # Print errors (if found)
        if errors:
            Printer.print_head("PARSING ERRORS")
            print(errors)

        parse_time = timeit.default_timer() - start_parse_time

        # Generate the term-by-user story matrix (m), and additional data in two other matrices
        start_matrix_time = timeit.default_timer()

        matrix = Matrix(self.base_weight, self.weights)
        matrices = matrix.generate(user_stories_lst, ' '.join([u.sentence for u in user_stories_lst]), nlp)
        m, count_matrix, stories_list, rme = matrices

        matr_time = timeit.default_timer() - start_matrix_time

        # Print details per user story, if argument '-u'/'--print_us' is chosen
        if self.print_us:
            print("Details:\n")
            for us in user_stories_lst:
                Printer.print_us_data(us)

        # Generate the ontology
        start_gen_time = timeit.default_timer()

        patterns = Constructor(nlp, user_stories_lst, m)
        out = patterns.make(self.system_name, self.threshold, self.link)
        output_ontology, output_prolog, output_ontobj, output_prologobj, onto_per_role = out

        # Print out the ontology in the terminal, if argument '-o'/'--print_ont' is chosen
        if self.print_ont:
            Printer.print_head("MANCHESTER OWL")
            print(output_ontology)

        gen_time = timeit.default_timer() - start_gen_time

        # Gather statistics and print the results
        stats_time = 0
        if self.statistics:
            start_stats_time = timeit.default_timer()

            stats_arr = Statistics.to_stats_array(user_stories_lst)

            Printer.print_head("USER STORY STATISTICS")
            Printer.print_stats(stats_arr[0], True)
            Printer.print_stats(stats_arr[1], True)
            Printer.print_subhead("Term - by - User Story Matrix ( Terms w/ total weight 0 hidden )")
            hide_zero = m[(m['sum'] > 0)]
            print(hide_zero)

            stats_time = timeit.default_timer() - start_stats_time

        # Writes output files
        writer = Writer()

        folder = "output/" + str(self.system_name)
        reports_folder = folder + "/reports"
        stats_folder = reports_folder + "/stats"

        outputfile = writer.make_file(folder + "/ontology", str(self.system_name), "omn", output_ontology)
        files = [["Manchester Ontology", outputfile]]

        if self.statistics:
            files.append(["General statistics", writer.make_file(stats_folder, str(self.system_name), "csv", stats_arr[0])])
            files.append(
                ["Term-by-User Story matrix",
                 writer.make_file(stats_folder, str(self.system_name) + "-term_by_US_matrix", "csv", m)])
            files.append(
                ["Sentence statistics", writer.make_file(stats_folder, str(self.system_name) + "-sentences", "csv", stats_arr[1])])
        if self.prolog:
            files.append(["Prolog", writer.make_file(folder + "/prolog", str(self.system_name), "pl", output_prolog)])
        if self.json:
            output_json_li = [str(us.toJSON()) for us in user_stories_lst]
            output_json = "\n".join(output_json_li)
            files.append(
                ["JSON", writer.make_file(folder + "/json", str(self.system_name) + "-user_stories", "json", output_json)])
        if self.per_role:
            for o in onto_per_role:
                files.append(["Individual Ontology for '" + str(o[0]) + "'",
                              writer.make_file(folder + "/ontology", str(self.system_name) + "-" + str(o[0]), "omn", o[1])])

        # Print the used ontology generation settings
        Printer.print_gen_settings(matrix, self.base_weight, self.threshold)

        # Print details of the generation
        Printer.print_details(fail, success, nlp_time, parse_time, matr_time, gen_time, stats_time)

        report_dict = {
            "stories": user_stories_lst,
            "failed_stories": failed_stories_lst,
            "systemname": self.system_name,
            "us_success": success,
            "us_fail": fail,
            "times": [["Initializing Natural Language Processor (<em>spaCy</em> v" + pkg_resources.get_distribution(
                "spacy").version + ")", nlp_time], ["Mining User Stories", parse_time],
                      ["Creating Factor Matrix", matr_time], ["Generating Manchester Ontology", gen_time],
                      ["Gathering statistics", stats_time]],
            "dir": os.path.dirname(os.path.realpath(__file__)),
            "inputfile": self.filename,
            "inputfile_lines": len(story_lines),
            "outputfiles": files,
            "threshold": self.threshold,
            "base": self.base_weight,
            "matrix": matrix,
            "weights": m['sum'].copy().reset_index().sort_values(['sum'], ascending=False).values.tolist(),
            "counts": count_matrix.reset_index().values.tolist(),
            "classes": output_ontobj.classes,
            "relationships": output_prologobj.relationships,
            "types": list(count_matrix.columns.values),
            "ontology": multiline(output_ontology)
        }

        # Finally, generate a report
        CURR_DIR = os.path.dirname(os.path.abspath(__file__))
        report = writer.make_file(
            reports_folder,
            str(self.system_name) + "_REPORT",
            "html",
            Generator.gen_report(str(CURR_DIR), report_dict)
        )
        files.append(["Report", report])

        # Print the location and name of all output files
        for file in files:
            if str(file[1]) != "":
                print(str(file[0]) + " file succesfully created at: \"" + str(file[1]) + "\"")

        # Return objects so that they can be used as input for other tools
        return {'us_instances': user_stories_lst, 'output_ontobj': output_ontobj, 'output_prologobj': output_prologobj,
                'matrix': m}