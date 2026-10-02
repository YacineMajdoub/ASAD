# bug_complexity_labels.py

import difflib
import math
import re
import numpy as np


KEYWORDS = {
    "python": {
        "def", "return", "if", "else", "elif", "for", "while", "try",
        "except", "with", "class", "import", "from", "as", "in", "is",
        "not", "and", "or", "lambda", "yield", "raise", "pass",
        "break", "continue", "assert", "del", "None", "True", "False"
    },
    "java": {
        "public", "private", "protected", "static", "final", "class",
        "interface", "extends", "implements", "return", "if", "else",
        "for", "while", "do", "switch", "case", "try", "catch",
        "finally", "throw", "throws", "new", "this", "super", "null",
        "true", "false", "void", "int", "long", "double", "float",
        "char", "boolean", "byte", "short", "import", "package",
        "instanceof", "synchronized", "volatile", "abstract"
    },
    "c": {
        "int", "char", "float", "double", "void", "long", "short",
        "unsigned", "signed", "struct", "union", "enum", "typedef",
        "return", "if", "else", "for", "while", "do", "switch",
        "case", "break", "continue", "goto", "sizeof", "static",
        "extern", "const", "volatile", "NULL"
    },
    "cpp": {
        "int", "char", "float", "double", "void", "long", "short",
        "unsigned", "signed", "struct", "union", "enum", "class",
        "public", "private", "protected", "virtual", "return", "if",
        "else", "for", "while", "do", "switch", "case", "break",
        "continue", "goto", "sizeof", "static", "extern", "const",
        "volatile", "new", "delete", "try", "catch", "throw",
        "namespace", "using", "template", "typename", "nullptr",
        "true", "false"
    }
}


OPERATOR_RE = re.compile(
    r"(==|!=|<=|>=|&&|\|\||\+\+|--|<<|>>|\+=|-=|\*=|/=|%=|->|::|"
    r"[+\-*/%=<>!&|^~?:;,.()\[\]{}])"
)

IDENT_RE = re.compile(r"[A-Za-z_]\w*")


def _clean_lines(code):
    lines = []

    for line in code.splitlines():
        line = re.sub(r"//.*$", "", line)
        line = re.sub(r"#.*$", "", line)

        if line.strip():
            lines.append(line.strip())

    return lines


def _halstead_effort(code, language):
    code = re.sub(r'"(?:[^"\\]|\\.)*"', ' "S" ', code)
    code = re.sub(r"'(?:[^'\\]|\\.)*'", " 'S' ", code)

    operators = OPERATOR_RE.findall(code)
    operands = []

    for token in IDENT_RE.findall(code):
        if token not in KEYWORDS.get(language, set()):
            operands.append(token)

    n1 = len(set(operators))
    n2 = len(set(operands))
    N1 = len(operators)
    N2 = len(operands)

    if n1 == 0 or n2 == 0:
        return 0.0

    vocabulary = n1 + n2
    length = N1 + N2

    volume = length * math.log2(vocabulary)
    difficulty = (n1 / 2) * (N2 / n2)

    return difficulty * volume


def _get_metrics(buggy, correct, language):
    buggy_lines = _clean_lines(buggy)
    correct_lines = _clean_lines(correct)

    matcher = difflib.SequenceMatcher(
        None,
        buggy_lines,
        correct_lines,
        autojunk=False
    )

    changed_lines = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            changed_lines.extend(buggy_lines[i1:i2])

    if not changed_lines and buggy_lines:
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "insert":
                changed_lines.append(buggy_lines[min(i1, len(buggy_lines) - 1)])

    region = "\n".join(changed_lines)

    return (
        len(changed_lines),
        _halstead_effort(region, language)
    )



def calibrate_thresholds(debugbench):
    """
    debugbench = list of:
        (buggy_code, correct_code, language, label)

    label must be: easy, medium, or hard.

    Run this ONCE before the experiments.
    """

    thresholds = {}

    for language in {x[2].lower() for x in debugbench}:
        data = {
            "easy": [],
            "medium": [],
            "hard": []
        }

        for buggy, correct, lang, label in debugbench:
            if lang.lower() != language:
                continue

            edit, effort = _get_metrics(buggy, correct, language)
            data[label.lower()].append((edit, effort))

        easy_edit = [x[0] for x in data["easy"]]
        medium_edit = [x[0] for x in data["medium"]]

        easy_effort = [x[1] for x in data["easy"]]
        medium_effort = [x[1] for x in data["medium"]]

        edit_boundary_1 = (
            np.percentile(easy_edit, 75)
            + np.percentile(medium_edit, 25)
        ) / 2

        effort_boundary_1 = (
            np.percentile(easy_effort, 75)
            + np.percentile(medium_effort, 25)
        ) / 2

        medium_edit_2 = [x[0] for x in data["medium"]]
        hard_edit = [x[0] for x in data["hard"]]

        medium_effort_2 = [x[1] for x in data["medium"]]
        hard_effort = [x[1] for x in data["hard"]]

        edit_boundary_2 = (
            np.percentile(medium_edit_2, 75)
            + np.percentile(hard_edit, 25)
        ) / 2

        effort_boundary_2 = (
            np.percentile(medium_effort_2, 75)
            + np.percentile(hard_effort, 25)
        ) / 2

        thresholds[language] = {
            "edit": (edit_boundary_1, edit_boundary_2),
            "effort": (effort_boundary_1, effort_boundary_2)
        }

    return thresholds



THRESHOLDS = {}


def classify_bug_complexity(buggy, correct, language):
    """
    Return: 'low', 'medium', or 'high'.

    buggy   = buggy source code
    correct = ground-truth fixed source code
    language = python / java / c / cpp
    """

    language = language.lower()

    if language not in THRESHOLDS:
        raise ValueError(
            f"No thresholds defined for language: {language}. "
            "Calibrate on DebugBench first."
        )

    edit, effort = _get_metrics(buggy, correct, language)

    edit_t1, edit_t2 = THRESHOLDS[language]["edit"]
    effort_t1, effort_t2 = THRESHOLDS[language]["effort"]

    edit_level = (
        "low" if edit <= edit_t1
        else "medium" if edit <= edit_t2
        else "high"
    )

    effort_level = (
        "low" if effort <= effort_t1
        else "medium" if effort <= effort_t2
        else "high"
    )

    order = {"low": 0, "medium": 1, "high": 2}

    return max(
        edit_level,
        effort_level,
        key=lambda x: order[x]
    )