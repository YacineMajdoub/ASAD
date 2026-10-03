"""
Moteur d'analyse statique et de métriques de complexité pour ASAD.
Supporte nativement une architecture polyglotte (Python, C, C++, Java)
grâce aux grammaires Tree-sitter modulaires.
"""

from collections import defaultdict
import re
from typing import Dict, Any, List, Optional, Set

from tree_sitter import Language, Parser

# Grammaires supportées avec chargement conditionnel (graceful fallback)
try:
    import tree_sitter_python
    HAS_TREE_SITTER_PYTHON = True
except ImportError:
    tree_sitter_python = None
    HAS_TREE_SITTER_PYTHON = False

try:
    import tree_sitter_c
    HAS_TREE_SITTER_C = True
except ImportError:
    tree_sitter_c = None
    HAS_TREE_SITTER_C = False

try:
    import tree_sitter_cpp
    HAS_TREE_SITTER_CPP = True
except ImportError:
    tree_sitter_cpp = None
    HAS_TREE_SITTER_CPP = False

try:
    import tree_sitter_java
    HAS_TREE_SITTER_JAVA = True
except ImportError:
    tree_sitter_java = None
    HAS_TREE_SITTER_JAVA = False


# =====================================================
# CACHE DES LANGAGES ET PARSEURS
# =====================================================

_PARSER_CACHE: Dict[str, Parser] = {}
_LANGUAGE_CACHE: Dict[str, Language] = {}


# =====================================================
# PROFILS DE LANGAGES
# =====================================================

LANGUAGE_PROFILES: Dict[str, Dict[str, Any]] = {
    "python": {
        "module": tree_sitter_python,
        "control_nodes": {
            "if_statement",
            "for_statement",
            "while_statement",
            "conditional_expression",
            "match_statement",
            "case_clause",
            "list_comprehension",
            "dict_comprehension",
            "set_comprehension",
            "generator_expression",
        },
        "function_nodes": {"function_definition"},
        "call_nodes": {"call"},
        "comment_prefixes": ("#",),
        "concurrency_keywords": [
            "thread",
            "threading",
            "asyncio",
            "multiprocessing",
            "concurrent",
            "coroutine",
            "task",
            "lock",
            "queue",
        ],
        "resource_apis": [
            "open",
            "close",
            "read",
            "write",
            "socket",
            "connect",
            "cursor",
            "session",
            "with open",
        ],
    },
    "c": {
        "module": tree_sitter_c,
        "control_nodes": {
            "if_statement",
            "for_statement",
            "while_statement",
            "do_statement",
            "case_statement",
            "switch_statement",
            "conditional_expression",
        },
        "function_nodes": {"function_definition"},
        "call_nodes": {"call_expression"},
        "comment_prefixes": ("//", "/*", "*"),
        "concurrency_keywords": [
            "pthread",
            "thread",
            "mutex",
            "semaphore",
            "atomic",
            "fork",
            "omp",
        ],
        "resource_apis": [
            "malloc",
            "calloc",
            "realloc",
            "free",
            "fopen",
            "fclose",
            "open",
            "close",
            "read",
            "write",
        ],
    },
    "cpp": {
        "module": tree_sitter_cpp if HAS_TREE_SITTER_CPP else tree_sitter_c,
        "control_nodes": {
            "if_statement",
            "for_statement",
            "while_statement",
            "do_statement",
            "case_statement",
            "switch_statement",
            "conditional_expression",
            "range_based_for_statement",
            "try_statement",
            "catch_clause",
        },
        "function_nodes": {"function_definition"},
        "call_nodes": {"call_expression"},
        "comment_prefixes": ("//", "/*", "*"),
        "concurrency_keywords": [
            "std::thread",
            "std::mutex",
            "pthread",
            "thread",
            "mutex",
            "semaphore",
            "atomic",
        ],
        "resource_apis": [
            "malloc",
            "calloc",
            "realloc",
            "free",
            "fopen",
            "fclose",
            "open",
            "close",
            "new",
            "delete",
            "ifstream",
            "ofstream",
        ],
    },
    "java": {
        "module": tree_sitter_java if HAS_TREE_SITTER_JAVA else tree_sitter_c,
        "control_nodes": {
            "if_statement",
            "for_statement",
            "enhanced_for_statement",
            "while_statement",
            "do_statement",
            "switch_block_statement_group",
            "switch_rule",
            "ternary_expression",
        },
        "function_nodes": {"method_declaration", "constructor_declaration", "function_definition"},
        "call_nodes": {"method_invocation", "call_expression"},
        "comment_prefixes": ("//", "/*", "*"),
        "concurrency_keywords": [
            "thread",
            "runnable",
            "synchronized",
            "executorservice",
            "semaphore",
            "atomic",
            "lock",
        ],
        "resource_apis": [
            "close",
            "autocloseable",
            "inputstream",
            "outputstream",
            "reader",
            "writer",
            "connection",
            "statement",
        ],
    },
}


# =====================================================
# DÉTECTION DU LANGAGE
# =====================================================

def detect_language(code: str, language_hint: Optional[str] = None) -> str:
    """
    Détecte automatiquement le langage source du code fourni.
    
    Args:
        code: Le code source à analyser
        language_hint: Indice explicite ("python", "c", "cpp", "java", "auto")
        
    Returns:
        Identifiant normalisé du langage ("python", "c", "cpp", "java")
    """
    if language_hint and language_hint.lower() not in ("auto", "unknown", ""):
        hint = language_hint.lower().strip()
        if hint in ("py", "python", "python3"):
            return "python"
        if hint in ("c",):
            return "c"
        if hint in ("cpp", "c++", "cxx", "cc"):
            return "cpp"
        if hint in ("java",):
            return "java"

    # Heuristique d'analyse de tokens
    scores = {"python": 0, "c": 0, "cpp": 0, "java": 0}

    # Motifs caractéristiques Python
    if re.search(r"^\s*(def\s+\w+|import\s+\w+|from\s+\w+\s+import|class\s+\w+.*:)", code, re.MULTILINE):
        scores["python"] += 5
    if re.search(r"\b(elif|True|False|None|self|__init__|__name__)\b", code):
        scores["python"] += 3
    if re.search(r"^\s*#(?!\s*include)", code, re.MULTILINE):
        scores["python"] += 2

    # Motifs caractéristiques Java
    if re.search(r"\b(public|private|protected)\s+(static\s+)?(class|void|int|boolean|String)\b", code):
        scores["java"] += 6
    if "System.out." in code:
        scores["java"] += 4

    # Motifs caractéristiques C / C++
    if re.search(r"#include\s*[<\"].*[>\"]", code):
        scores["c"] += 4
        scores["cpp"] += 4
    if re.search(r"\b(std::|cout|cin|vector<|string\s+\w+)", code):
        scores["cpp"] += 6
    if re.search(r"\b(int\s+main\s*\(|printf\s*\(|malloc\s*\(|free\s*\()", code):
        scores["c"] += 4

    # Sélection du langage avec le meilleur score
    best_lang, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score > 0:
        return best_lang

    # Par défaut : Python si présence de deux-points ou indentation typique, sinon C
    if ":" in code and ("def " in code or "for " in code):
        return "python"

    return "c"


# =====================================================
# AST SETUP & FACTORY
# =====================================================

def get_parser_for_language(language: str) -> Parser:
    """Récupère ou instancie le parseur Tree-sitter adapté au langage."""
    lang_key = language.lower()
    if lang_key not in LANGUAGE_PROFILES:
        lang_key = "c"

    if lang_key in _PARSER_CACHE:
        return _PARSER_CACHE[lang_key]

    profile = LANGUAGE_PROFILES[lang_key]
    module = profile.get("module")

    # Fallback si le module dédié n'est pas disponible
    if module is None:
        module = tree_sitter_c

    try:
        ts_lang = Language(module.language())
        parser = Parser(ts_lang)
    except (TypeError, AttributeError):
        parser = Parser()
        ts_lang = Language(module.language())
        parser.set_language(ts_lang)

    _PARSER_CACHE[lang_key] = parser
    _LANGUAGE_CACHE[lang_key] = ts_lang
    return parser


# Parseur C par défaut pour rétro-compatibilité avec les scripts externes
C_LANGUAGE = Language(tree_sitter_c.language()) if HAS_TREE_SITTER_C else None
try:
    parser = Parser(C_LANGUAGE) if C_LANGUAGE else Parser()
except (TypeError, AttributeError):
    parser = Parser()
    if C_LANGUAGE:
        parser.set_language(C_LANGUAGE)


# =====================================================
# AST HELPERS
# =====================================================

def walk(node):
    """Générateur parcourant tous les nœuds de l'arbre syntaxique."""
    yield node
    for child in node.children:
        yield from walk(child)


def ast_depth(node):
    """Calcule la profondeur maximale du nœud AST."""
    depth = 0
    while node.parent:
        depth += 1
        node = node.parent
    return depth


def ast_branching_factor(root):
    """Calcule le facteur de branchement moyen de l'AST."""
    values = []
    for node in walk(root):
        if len(node.children) > 1:
            values.append(len(node.children))

    return sum(values) / len(values) if values else 0


# =====================================================
# SOURCE METRICS
# =====================================================

def calculate_nloc(code: str, language: str = "c") -> int:
    """
    Calcule le nombre de lignes de code effectives (hors commentaires et lignes vides),
    en tenant compte de la syntaxe des commentaires propre au langage.
    """
    lang_key = language.lower() if language else "c"
    profile = LANGUAGE_PROFILES.get(lang_key, LANGUAGE_PROFILES["c"])
    comment_prefixes = profile.get("comment_prefixes", ("//", "/*", "*"))

    count = 0
    in_multiline_docstring = False

    for line in code.splitlines():
        line = line.strip()
        if not line:
            continue

        # Gestion des docstrings multilignes Python
        if lang_key == "python":
            if line.startswith('"""') or line.startswith("'''"):
                if line.count('"""') == 2 or line.count("'''") == 2:
                    continue
                in_multiline_docstring = not in_multiline_docstring
                continue
            if in_multiline_docstring:
                if '"""' in line or "'''" in line:
                    in_multiline_docstring = False
                continue

        # Filtrage des commentaires mono-lignes
        is_comment = False
        for prefix in comment_prefixes:
            if line.startswith(prefix):
                is_comment = True
                break

        if not is_comment:
            count += 1

    return count


def calculate_cyclomatic_complexity(root, language: str = "c") -> int:
    """
    Calcule la complexité cyclomatique de McCabe en comptabilisant
    les nœuds de branchement spécifiques à la grammaire du langage.
    """
    lang_key = language.lower() if language else "c"
    profile = LANGUAGE_PROFILES.get(lang_key, LANGUAGE_PROFILES["c"])
    control_nodes: Set[str] = profile.get("control_nodes", set())

    complexity = 1
    for node in walk(root):
        if node.type in control_nodes:
            complexity += 1

    return complexity


# =====================================================
# FUNCTION DEPENDENCIES & CALL GRAPH
# =====================================================

def extract_calls(root, language: str = "c") -> Dict[str, List[str]]:
    """
    Construit le graphe d'appels inter-fonctions adapté à l'AST du langage.
    """
    lang_key = language.lower() if language else "c"
    profile = LANGUAGE_PROFILES.get(lang_key, LANGUAGE_PROFILES["c"])
    function_nodes: Set[str] = profile.get("function_nodes", {"function_definition"})
    call_nodes: Set[str] = profile.get("call_nodes", {"call_expression"})

    calls = defaultdict(list)
    current_function: Optional[str] = None

    for node in walk(root):
        if node.type in function_nodes:
            # Récupération du nom de la fonction
            fn_name = None
            name_child = node.child_by_field_name("name") or node.child_by_field_name("declarator")
            if name_child:
                ids = [n.text.decode("utf-8", errors="ignore") for n in walk(name_child) if n.type == "identifier"]
                if ids:
                    fn_name = ids[0]
            if not fn_name:
                ids = [n.text.decode("utf-8", errors="ignore") for n in walk(node) if n.type == "identifier"]
                if ids:
                    fn_name = ids[0]

            if fn_name:
                current_function = fn_name
                if current_function not in calls:
                    calls[current_function] = []

        elif node.type in call_nodes and current_function:
            # Récupération de la cible de l'appel
            target_name = None
            fn_target = node.child_by_field_name("function")
            if fn_target:
                ids = [n.text.decode("utf-8", errors="ignore") for n in walk(fn_target) if n.type == "identifier"]
                if ids:
                    target_name = ids[-1]
            if not target_name:
                ids = [n.text.decode("utf-8", errors="ignore") for n in walk(node) if n.type == "identifier"]
                if ids:
                    target_name = ids[0]

            if target_name:
                calls[current_function].append(target_name)

    return calls


def dependency_metrics(root, language: str = "c") -> Dict[str, Any]:
    """Calcule les métriques de couplage (fan-in, fan-out, nombre de fonctions)."""
    calls = extract_calls(root, language=language)

    fan_in = defaultdict(int)
    fan_out = {}

    for func, targets in calls.items():
        unique_targets = set(targets)
        fan_out[func] = len(unique_targets)
        for target in unique_targets:
            fan_in[target] += 1

    return {
        "average_fan_in": (sum(fan_in.values()) / len(fan_in)) if fan_in else 0.0,
        "average_fan_out": (sum(fan_out.values()) / len(fan_out)) if fan_out else 0.0,
        "number_of_functions": len(calls),
    }


# =====================================================
# SYSTEM LEVEL OPERATIONS
# =====================================================

def analyze_system_operations(code: str, language: str = "c") -> Dict[str, Any]:
    """
    Détecte les primitives de concurrence et de gestion de ressources
    adaptées au langage analysé.
    """
    lang_key = language.lower() if language else "c"
    profile = LANGUAGE_PROFILES.get(lang_key, LANGUAGE_PROFILES["c"])
    concurrency_kw = profile.get("concurrency_keywords", [])
    resource_kw = profile.get("resource_apis", [])

    lower = code.lower()

    concurrency = [x for x in concurrency_kw if x in lower]
    resources = [x for x in resource_kw if x in lower]

    return {
        "concurrency_detected": bool(concurrency),
        "concurrency_constructs": concurrency,
        "resource_management_detected": bool(resources),
        "resource_APIs": resources,
    }


# =====================================================
# ERROR SEVERITY (OPTIONAL)
# =====================================================

def analyze_errors(
    failing_tests=None,
    runtime_error=None,
    compilation_error=None
) -> Dict[str, Any]:
    """Structure les signaux d'erreurs d'exécution ou de compilation."""
    return {
        "available": any([
            failing_tests is not None,
            runtime_error is not None,
            compilation_error is not None
        ]),
        "failing_tests": failing_tests,
        "runtime_error": runtime_error,
        "compilation_error": compilation_error
    }


# =====================================================
# MAIN CALLABLE CLASS
# =====================================================

class CodeComplexityAnalyzer:
    """
    Analyseur statique polyglotte pour ASAD.
    Fournit les signaux de complexité indispensables au routage d'agents.
    """

    def __init__(self, default_language: str = "auto"):
        self.default_language = default_language

    def analyze(
        self,
        buggy_code: str,
        language: str = "auto",
        failing_tests=None,
        runtime_error=None,
        compilation_error=None
    ) -> Dict[str, Any]:
        """
        Analyse le code source fourni et produit le rapport complet de complexité.

        Args:
            buggy_code: Code source contenant le bogue
            language: "auto" pour détection automatique, ou nom explicite ("python", "c", etc.)
            failing_tests: Logs de tests échoués éventuels
            runtime_error: Erreur d'exécution éventuelle
            compilation_error: Erreur de compilation éventuelle

        Returns:
            Rapport hiérarchique de complexité pour le Main Analysis Agent
        """
        # Résolution du langage
        target_lang = self.default_language if language == "auto" else language
        detected_lang = detect_language(buggy_code, language_hint=target_lang)

        # Parse de l'arbre syntaxique avec le parseur adapté
        active_parser = get_parser_for_language(detected_lang)
        tree = active_parser.parse(bytes(buggy_code, "utf8"))
        root = tree.root_node

        report = {
            "detected_language": detected_lang,

            "error_severity": analyze_errors(
                failing_tests=failing_tests,
                runtime_error=runtime_error,
                compilation_error=compilation_error
            ),

            "source_location_difficulty": {
                "NLOC": calculate_nloc(buggy_code, language=detected_lang),
                "AST_depth": ast_depth(root),
            },

            "program_understanding_difficulty": {
                "cyclomatic_complexity": calculate_cyclomatic_complexity(root, language=detected_lang),
                "AST_branching_factor": ast_branching_factor(root),
            },

            "system_level_operations": analyze_system_operations(buggy_code, language=detected_lang),

            "inter_function_dependencies": dependency_metrics(root, language=detected_lang),
        }

        return report