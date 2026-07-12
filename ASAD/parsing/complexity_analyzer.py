<<<<<<< HEAD:Scripts/parsing/complexity_analyzer.py
from tree_sitter import Language, Parser
import tree_sitter_c
from collections import defaultdict


# =====================================================
# AST SETUP
# =====================================================

C_LANGUAGE = Language(tree_sitter_c.language())

parser = Parser()
parser.set_language(C_LANGUAGE)



# =====================================================
# CONSTANTS
# =====================================================

CONTROL_NODES = {
    "if_statement",
    "for_statement",
    "while_statement",
    "do_statement",
    "case_statement",
    "switch_statement",
    "conditional_expression"
}


CONCURRENCY_KEYWORDS = [
    "pthread",
    "thread",
    "mutex",
    "semaphore",
    "atomic",
    "fork",
    "omp"
]


RESOURCE_APIS = [
    "malloc",
    "calloc",
    "realloc",
    "free",
    "fopen",
    "fclose",
    "open",
    "close",
    "read",
    "write"
]



# =====================================================
# AST HELPERS
# =====================================================

def walk(node):

    yield node

    for child in node.children:
        yield from walk(child)



def ast_depth(node):

    depth = 0

    while node.parent:
        depth += 1
        node = node.parent

    return depth



def ast_branching_factor(root):

    values = []

    for node in walk(root):

        if len(node.children) > 1:
            values.append(len(node.children))


    return (
        sum(values) / len(values)
        if values else 0
    )



# =====================================================
# SOURCE METRICS
# =====================================================

def calculate_nloc(code):

    count = 0

    for line in code.splitlines():

        line = line.strip()

        if (
            line
            and not line.startswith("//")
            and not line.startswith("*")
            and not line.startswith("/*")
        ):
            count += 1

    return count



def calculate_cyclomatic_complexity(root):

    complexity = 1

    for node in walk(root):

        if node.type in CONTROL_NODES:
            complexity += 1


    return complexity



# =====================================================
# FUNCTION DEPENDENCIES
# =====================================================

def extract_calls(root):

    calls = defaultdict(list)

    current_function = None


    for node in walk(root):

        if node.type == "function_definition":

            ids = [
                n.text.decode()
                for n in walk(node)
                if n.type == "identifier"
            ]

            if ids:
                current_function = ids[0]


        elif node.type == "call_expression":

            ids = [
                n.text.decode()
                for n in walk(node)
                if n.type == "identifier"
            ]

            if ids and current_function:

                calls[current_function].append(ids[0])


    return calls



def dependency_metrics(root):

    calls = extract_calls(root)

    fan_in = defaultdict(int)
    fan_out = {}


    for func, targets in calls.items():

        unique_targets = set(targets)

        fan_out[func] = len(unique_targets)

        for target in unique_targets:
            fan_in[target] += 1


    return {

        "average_fan_in":
            sum(fan_in.values()) / len(fan_in)
            if fan_in else 0,


        "average_fan_out":
            sum(fan_out.values()) / len(fan_out)
            if fan_out else 0,


        "number_of_functions":
            len(calls)

    }



# =====================================================
# SYSTEM LEVEL OPERATIONS
# =====================================================

def analyze_system_operations(code):

    lower = code.lower()


    concurrency = [
        x for x in CONCURRENCY_KEYWORDS
        if x in lower
    ]


    resources = [
        x for x in RESOURCE_APIS
        if x in lower
    ]


    return {

        "concurrency_detected":
            bool(concurrency),

        "concurrency_constructs":
            concurrency,


        "resource_management_detected":
            bool(resources),

        "resource_APIs":
            resources

    }



# =====================================================
# ERROR SEVERITY (OPTIONAL)
# =====================================================

def analyze_errors(
        failing_tests=None,
        runtime_error=None,
        compilation_error=None):


    return {

        "available":
            any([
                failing_tests is not None,
                runtime_error is not None,
                compilation_error is not None
            ]),


        "failing_tests":
            failing_tests,


        "runtime_error":
            runtime_error,


        "compilation_error":
            compilation_error
    }



# =====================================================
# MAIN CALLABLE CLASS
# =====================================================

class CodeComplexityAnalyzer:


    def __init__(self):

        self.parser = parser



    def analyze(
            self,
            buggy_code,
            failing_tests=None,
            runtime_error=None,
            compilation_error=None):


        tree = self.parser.parse(
            bytes(
                buggy_code,
                "utf8"
            )
        )


        root = tree.root_node


        report = {


            "error_severity":
                analyze_errors(
                    failing_tests,
                    runtime_error,
                    compilation_error
                ),


            "source_location_difficulty": {

                "NLOC":
                    calculate_nloc(
                        buggy_code
                    ),

                "AST_depth":
                    ast_depth(root)

            },


            "program_understanding_difficulty": {

                "cyclomatic_complexity":
                    calculate_cyclomatic_complexity(root),


                "AST_branching_factor":
                    ast_branching_factor(root)

            },


            "system_level_operations":
                analyze_system_operations(
                    buggy_code
                ),


            "inter_function_dependencies":
                dependency_metrics(root)

        }


=======
from tree_sitter import Language, Parser
import tree_sitter_c
from collections import defaultdict


# =====================================================
# AST SETUP
# =====================================================

C_LANGUAGE = Language(tree_sitter_c.language())

parser = Parser()
parser.set_language(C_LANGUAGE)



# =====================================================
# CONSTANTS
# =====================================================

CONTROL_NODES = {
    "if_statement",
    "for_statement",
    "while_statement",
    "do_statement",
    "case_statement",
    "switch_statement",
    "conditional_expression"
}


CONCURRENCY_KEYWORDS = [
    "pthread",
    "thread",
    "mutex",
    "semaphore",
    "atomic",
    "fork",
    "omp"
]


RESOURCE_APIS = [
    "malloc",
    "calloc",
    "realloc",
    "free",
    "fopen",
    "fclose",
    "open",
    "close",
    "read",
    "write"
]



# =====================================================
# AST HELPERS
# =====================================================

def walk(node):

    yield node

    for child in node.children:
        yield from walk(child)



def ast_depth(node):

    depth = 0

    while node.parent:
        depth += 1
        node = node.parent

    return depth



def ast_branching_factor(root):

    values = []

    for node in walk(root):

        if len(node.children) > 1:
            values.append(len(node.children))


    return (
        sum(values) / len(values)
        if values else 0
    )



# =====================================================
# SOURCE METRICS
# =====================================================

def calculate_nloc(code):

    count = 0

    for line in code.splitlines():

        line = line.strip()

        if (
            line
            and not line.startswith("//")
            and not line.startswith("*")
            and not line.startswith("/*")
        ):
            count += 1

    return count



def calculate_cyclomatic_complexity(root):

    complexity = 1

    for node in walk(root):

        if node.type in CONTROL_NODES:
            complexity += 1


    return complexity



# =====================================================
# FUNCTION DEPENDENCIES
# =====================================================

def extract_calls(root):

    calls = defaultdict(list)

    current_function = None


    for node in walk(root):

        if node.type == "function_definition":

            ids = [
                n.text.decode()
                for n in walk(node)
                if n.type == "identifier"
            ]

            if ids:
                current_function = ids[0]


        elif node.type == "call_expression":

            ids = [
                n.text.decode()
                for n in walk(node)
                if n.type == "identifier"
            ]

            if ids and current_function:

                calls[current_function].append(ids[0])


    return calls



def dependency_metrics(root):

    calls = extract_calls(root)

    fan_in = defaultdict(int)
    fan_out = {}


    for func, targets in calls.items():

        unique_targets = set(targets)

        fan_out[func] = len(unique_targets)

        for target in unique_targets:
            fan_in[target] += 1


    return {

        "average_fan_in":
            sum(fan_in.values()) / len(fan_in)
            if fan_in else 0,


        "average_fan_out":
            sum(fan_out.values()) / len(fan_out)
            if fan_out else 0,


        "number_of_functions":
            len(calls)

    }



# =====================================================
# SYSTEM LEVEL OPERATIONS
# =====================================================

def analyze_system_operations(code):

    lower = code.lower()


    concurrency = [
        x for x in CONCURRENCY_KEYWORDS
        if x in lower
    ]


    resources = [
        x for x in RESOURCE_APIS
        if x in lower
    ]


    return {

        "concurrency_detected":
            bool(concurrency),

        "concurrency_constructs":
            concurrency,


        "resource_management_detected":
            bool(resources),

        "resource_APIs":
            resources

    }



# =====================================================
# ERROR SEVERITY (OPTIONAL)
# =====================================================

def analyze_errors(
        failing_tests=None,
        runtime_error=None,
        compilation_error=None):


    return {

        "available":
            any([
                failing_tests is not None,
                runtime_error is not None,
                compilation_error is not None
            ]),


        "failing_tests":
            failing_tests,


        "runtime_error":
            runtime_error,


        "compilation_error":
            compilation_error
    }



# =====================================================
# MAIN CALLABLE CLASS
# =====================================================

class CodeComplexityAnalyzer:


    def __init__(self):

        self.parser = parser



    def analyze(
            self,
            buggy_code,
            failing_tests=None,
            runtime_error=None,
            compilation_error=None):


        tree = self.parser.parse(
            bytes(
                buggy_code,
                "utf8"
            )
        )


        root = tree.root_node


        report = {


            "error_severity":
                analyze_errors(
                    failing_tests,
                    runtime_error,
                    compilation_error
                ),


            "source_location_difficulty": {

                "NLOC":
                    calculate_nloc(
                        buggy_code
                    ),

                "AST_depth":
                    ast_depth(root)

            },


            "program_understanding_difficulty": {

                "cyclomatic_complexity":
                    calculate_cyclomatic_complexity(root),


                "AST_branching_factor":
                    ast_branching_factor(root)

            },


            "system_level_operations":
                analyze_system_operations(
                    buggy_code
                ),


            "inter_function_dependencies":
                dependency_metrics(root)

        }


>>>>>>> fcfd7e0596eb45f42f661fae45b216a34d480234:asad/parsing/complexity_analyzer.py
        return report