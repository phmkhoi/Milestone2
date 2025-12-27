mock_data = {
    "elements": {
        "root_doc": "Document Root",
        "sec_intro": "1. Introduction",
        "text_001": "Deep learning is popular",
        "text_002": "It solves many problems.",
        "text_003": "However, it is costly",
        "math_001": "\\begin{equation} E=mc^2 \\end{equation}",
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

# def preprocessing(data_object: object):
#     map_value_key = {}
#     map_key_new_key_old = {}

#     for key, value in data_object['elements'].items():
#         if "\\begin{equation}" in value and "\\end{equation}" in value:
#             value = value.replace("\\begin{equation}", "$$").replace("\\end{equation}", "$$")
#             data_object['elements'][key] = value
#         if value in map_value_key:
#             map_key_new_key_old[key] = map_value_key[value]
#         else:
#             map_value_key[value] = key

#     for content_id in data_object['hierarchy'].values():
#         for key in map_key_new_key_old:
#             content_id.pop(key, None)
#             data_object['elements'].pop(key, None)
    
#     return data_object






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
    pass