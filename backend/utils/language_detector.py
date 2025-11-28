import re

def detect_language(code: str, provided_language: str = None) -> str:
    """Detect programming language from code content"""
    
    # If language is explicitly provided and seems reasonable, use it
    if provided_language and provided_language in ['python', 'javascript', 'java', 'cpp', 'typescript', 'go', 'rust']:
        return provided_language
    
    # Language detection patterns
    patterns = {
        'python': [
            r'def\s+\w+\s*\(',
            r'import\s+\w+',
            r'from\s+\w+\s+import',
            r'if\s+__name__\s*==\s*["\']__main__["\']',
            r'print\s*\(',
            r':\s*$'  # Python's colon syntax
        ],
        'javascript': [
            r'function\s+\w+\s*\(',
            r'var\s+\w+\s*=',
            r'let\s+\w+\s*=',
            r'const\s+\w+\s*=',
            r'=>',
            r'console\.log\s*\(',
            r'require\s*\(',
            r'module\.exports'
        ],
        'typescript': [
            r'interface\s+\w+',
            r'type\s+\w+\s*=',
            r':\s*\w+\s*=',  # Type annotations
            r'export\s+interface',
            r'import.*from.*["\'].*["\']'
        ],
        'java': [
            r'public\s+class\s+\w+',
            r'public\s+static\s+void\s+main',
            r'System\.out\.println',
            r'import\s+java\.',
            r'@\w+',  # Annotations
            r'public\s+\w+\s+\w+\s*\('
        ],
        'cpp': [
            r'#include\s*<.*>',
            r'std::',
            r'cout\s*<<',
            r'cin\s*>>',
            r'int\s+main\s*\(',
            r'using\s+namespace\s+std'
        ],
        'go': [
            r'package\s+\w+',
            r'import\s*\(',
            r'func\s+\w+\s*\(',
            r'fmt\.Print',
            r'go\s+\w+\s*\(',
            r'var\s+\w+\s+\w+'
        ],
        'rust': [
            r'fn\s+\w+\s*\(',
            r'let\s+mut\s+\w+',
            r'println!\s*\(',
            r'use\s+std::',
            r'impl\s+\w+',
            r'match\s+\w+'
        ]
    }
    
    # Count matches for each language
    scores = {}
    for language, lang_patterns in patterns.items():
        score = 0
        for pattern in lang_patterns:
            matches = len(re.findall(pattern, code, re.MULTILINE | re.IGNORECASE))
            score += matches
        scores[language] = score
    
    # Find the language with the highest score
    if scores:
        detected = max(scores, key=scores.get)
        if scores[detected] > 0:
            return detected
    
    # Fallback based on simple heuristics
    if 'def ' in code and ':' in code:
        return 'python'
    elif 'function' in code or '=>' in code:
        return 'javascript'
    elif 'public class' in code:
        return 'java'
    elif '#include' in code:
        return 'cpp'
    
    # Default fallback
    return provided_language or 'javascript'