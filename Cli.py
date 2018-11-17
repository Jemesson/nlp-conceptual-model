import os.path
from argparse import ArgumentParser
from ModelGenerationCli import ModelGenerationFromCli


def program(*args):
    """
    command execution
    :param args: command args
    :return: args
    """
    parameters = ArgumentParser(
        usage="""Cli.py <INPUT FILE> [<args>]
        
///////////////////////////////////////////
//              Visual Narrator          //
///////////////////////////////////////////

This program has multiple functionalities:
    (1) Mine user story information
    (2) Generate an ontology from a user story set
    (3) Generate Prolog from a user story set (including links to 'role', 'means' and 'ends')
    (4) Get statistics for a user story set
""", epilog="{*} Utrecht University. M.J. Robeer, 2015-2017")

    if "--return-args" not in args:
        parameters.add_argument(
            "filename",
            help="input file with user stories", metavar="INPUT FILE",
            type=lambda x: is_valid_file(parameters, x)
        )

    parameters.add_argument('--version', action='version', version='Visual Narrator v0.9 BETA by M.J. Robeer')

    general_param = parameters.add_argument_group("general arguments (optional)")
    general_param.add_argument("-n", "--name", dest="system_name",
                                    help="your system name, as used in ontology and output file(s) generation",
                                    required=False)
    general_param.add_argument("-u", "--print_us", dest="print_us",
                                    help="print data per user story in the console", action="store_true", default=False)
    general_param.add_argument("-o", "--print_ont", dest="print_ont",
                                    help="print ontology in the console", action="store_true", default=False)
    general_param.add_argument("-l", "--link", dest="link",
                                    help="link ontology classes to user story they originate from",
                                    action="store_true", default=False)
    general_param.add_argument("--prolog", dest="prolog", help="generate prolog output (.pl)",
                                    action="store_true", default=False)
    general_param.add_argument("--return-args", dest="return_args", help="return arguments instead of call VN",
                                    action="store_true", default=False)
    general_param.add_argument("--json", dest="json", help="export user stories as json (.json)",
                                    action="store_true", default=False)

    statistics_param = parameters.add_argument_group("statistics arguments (optional)")
    statistics_param.add_argument("-s", "--statistics", dest="statistics",
                     help="show user story set statistics and output these to a .csv file", action="store_true",
                     default=False)

    model_generation_param = parameters.add_argument_group("conceptual model generation tuning (optional)")
    model_generation_param.add_argument("-p", "--per_role", dest="per_role",
                                             help="create an additional conceptual model per role",
                                             action="store_true", default=False)
    model_generation_param.add_argument("-t", dest="threshold",
                                             help="set threshold for conceptual model generation (INT, default = 1.0)",
                                             type=float, default=1.0)
    model_generation_param.add_argument("-b", dest="base_weight", help="set the base weight (INT, default = 1)",
                                             type=int, default=1)
    model_generation_param.add_argument("-wfr", dest="weight_func_role",
                                             help="weight of functional role (FLOAT, default = 1.0)",
                                             type=float, default=1)
    model_generation_param.add_argument("-wdo", dest="weight_main_obj",
                                             help="weight of main object (FLOAT, default = 1.0)", type=float,
                                             default=1)
    model_generation_param.add_argument("-wffm", dest="weight_ff_means",
                                        help="weight of noun in free form means (FLOAT, default = 0.7)",
                                        type=float, default=0.7)
    model_generation_param.add_argument("-wffe", dest="weight_ff_ends",
                                        help="weight of noun in free form ends (FLOAT, default = 0.5)",
                                        type=float, default=0.5)
    model_generation_param.add_argument("-wcompound", dest="weight_compound",
                                        help="weight of nouns in compound compared to head (FLOAT, default = 0.66)",
                                        type=float, default=0.66)

    if len(args) < 1:
        args = parameters.parse_args()
    else:
        args = parameters.parse_args(args)

    # conceptual model weight given from arguments
    weights = [args.weight_func_role, args.weight_main_obj, args.weight_ff_means, args.weight_ff_ends,
               args.weight_compound]

    if not args.system_name or args.system_name == '':
        args.system_name = "Conceptual-Model-System"
    if not args.return_args:
        conceptual_model = ModelGenerationFromCli(args, weights)
        return conceptual_model.gen_concept_model()
    else:
        return args


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("Could not find file " + str(arg) + "!")
    else:
        return open(arg, 'r')


if __name__ == "__main__":
    program()
