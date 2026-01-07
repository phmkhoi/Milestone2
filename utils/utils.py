import os
import re
import shutil

def find_root_file(directory):
    for _, _, files in os.walk(directory):
        considered_files = []
        for file in files:
            if file.endswith('.tex'):
                path = os.path.normpath(os.path.join(directory, file))
                
                if not os.path.isfile(path):
                    continue
                
                with open(path, 'r', encoding='utf-8', errors='ignore') as fr:
                    content = fr.read()
                    if r'\begin{document}' in content:
                        pattern = r'\\(?:input|include)\b\{?([^}\s%]+)\}?'
                        match_lists = re.findall(pattern, content)
                        considered_files.append((path, len(match_lists)))
        
        if considered_files:
            return max(considered_files, key=lambda x: x[1])[0]
             
    return None


def gather_files(current_file_path, parent_dir_name=None, collected_path_lists=None):
    if collected_path_lists is None:
        collected_path_lists = []
    
    if parent_dir_name is None:
        parent_dir_name = os.path.dirname(current_file_path)
    else:
        current_file_path = os.path.normpath(os.path.join(parent_dir_name, current_file_path))
    
    if current_file_path in collected_path_lists or not os.path.exists(current_file_path):
        return collected_path_lists
    
    collected_path_lists.append(current_file_path)
    
    with open(current_file_path, 'r', encoding='utf-8', errors='ignore') as fr:
        content = re.sub(r'%.*', '', fr.read())
        
        pattern = r'\\(?:input|include)\b\{?([^}\s%]+)\}?'
        match_lists = re.findall(pattern, content)
        
        for file_name in match_lists:
            
            if not file_name.endswith('.tex'):
                file_name += '.tex'
                
            gather_files(file_name, parent_dir_name, collected_path_lists)
            
    return collected_path_lists


def get_document_body(raw_content):
    start_tag = r'\begin{document}'
    end_tag = r'\end{document}'
    
    start_idx = raw_content.find(start_tag)
    end_idx = raw_content.find(end_tag)
    
    if start_idx == -1:
        return ''
    
    if end_idx == -1:
        end_idx = len(raw_content)
    
    return raw_content[start_idx + len(start_tag):end_idx]


def get_paper_content(current_file_path, parent_dir_name=None):
    if parent_dir_name is None:
        parent_dir_name = os.path.dirname(current_file_path)
    else:
        current_file_path = os.path.normpath(os.path.join(parent_dir_name, current_file_path))
    
    if not os.path.exists(current_file_path):
        return f'% File {current_file_path} not found'
    
    with open(current_file_path, 'r', encoding='utf-8', errors='ignore') as fr:
        content = re.sub(r'(?<!\\)%.*', '', fr.read())
        
    INPUT_PATTERN = r'\\(?:input|include)\b\{?([^}\s%]+)\}?'
    
    def replace_content(match):
        included_file_name = match.group(1).strip()
        
        if not included_file_name.endswith('.tex'):
            included_file_name += '.tex'
        
        return get_paper_content(included_file_name, parent_dir_name)
    
    return re.sub(INPUT_PATTERN, replace_content, content)


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


def remove_tex_folder(folder_path: str) -> None:
    dirs = os.listdir(folder_path)
    
    for dir in dirs:
        tex_path = os.path.join(folder_path, dir, 'tex')
        shutil.rmtree(tex_path)
        
        
def count_ref_file(folder_path: str) -> int:
    dirs = os.listdir(folder_path)
    cnt = 0
    
    for dir in dirs:
        refs_path = os.path.join(folder_path, dir, 'refs.bib')
        
        if os.path.isfile(refs_path):
            cnt += 1
            
    return cnt