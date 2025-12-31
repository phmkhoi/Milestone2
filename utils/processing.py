import re
import json
mock_data = {
    "elements": {
        "root_doc": "Document Root",
        "sec_intro": "1. Introduction",
        "text_001": "Deep learning is popular",
        "text_002": "It solves many problems.",
        "text_003": "However, it is costly",
        "math_001": r"Consider \( f(x) = x^2 \). The integral is \[ \int f(x) dx = \frac{x^3}{3} + C \]. Note that \begin{math}C\end{math} is constant.",
        "text_004": "However, it is costly"
    },
    "hierarchy": {
        "1": {
            "sec_intro": "root_doc",
            "text_001": "sec_intro",
            "text_002": "sec_intro"
        },
        "2": {
            "sec_intro": "root_doc",
            "text_001": "sec_intro",
            "text_002": "sec_intro",
            "text_003": "sec_intro",
            "math_001": "sec_intro",
            "text_004": "sec_intro",
        }
    }
}

def preprocessing(data_object: object):
    map_value_key = {}
    map_key_new_key_old = {}

    for key, value in data_object['elements'].items():
        value = normalize_equation(value)
        data_object['elements'][key] = value
        if value in map_value_key:
            map_key_new_key_old[key] = map_value_key[value]
        else:
            map_value_key[value] = key

    for content_id in data_object['hierarchy'].values():
        for key in map_key_new_key_old:
            content_id.pop(key, None)
            data_object['elements'].pop(key, None)
    
    return data_object






# Some block equations syntax in tex
# \[...\], \begin{equation}...\end{equation}, \begin{align}...\end{align}, \begin{align*}...\end{align*}, $$...$$

# Inline equations syntax in tex. Always notice that inline equations can appear within the text
# \(...\), $...$, \begin{math}...\end{math}

# Using this command to test the function
# python -m unittest tests/test_normalization.py

def normalize_equation(text: str) -> str:
    '''
        This function is used to normalize the equation text.
        Convert to $$ if it is an inline mathematics, to \\begin{equation}...\\end{equation} if it is a block mathematics
    '''
    def replace(match):
        replace.i += 1
        if replace.i % 2 == 1:
            return r'\begin{equation}'
        else:
            return r'\end{equation}'
        
    inline_math = [
        (r"\(", r'\)'),
        (r"\begin{math}", r"\end{math}")
    ]
    display_math = [
        (r"$$", r"$$"),
        (r"\[", r"\]"),
        (r"\begin{align}", r"\end{align}"),
        (r"\begin{align*}", r"\end{align*}"),
        (r"\begin{equation*}", r"\end{equation*}")
    ]
    
    for formula in display_math:
        first_formula = formula[0]
        second_formula = formula[1]
        
        if first_formula == "$$":
            replace.i = 0
            text = re.sub(r"\$\$", replace, text)
        if first_formula in text and second_formula in text:
            text = text.replace(first_formula, r"\begin{equation}").replace(second_formula, r"\end{equation}")
    
    for formula in inline_math:
        first_formula = formula[0]
        second_formula = formula[1]
        
        if first_formula in text and second_formula in text:
            text = text.replace(first_formula, "$").replace(second_formula, "$")
    
    return text


# print(json.dumps(preprocessing(mock_data), indent=4))