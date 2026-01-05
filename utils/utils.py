import os
import re

def find_root_file(directory):
    for _, _, files in os.walk(directory):
        considered_files = []
        for file in files:
            if file.endswith('.tex'):
                path = os.path.normpath(os.path.join(directory, file))
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
        
        
    input_pattern = r'\\(?:input|include)\b\{?([^}\s%]+)\}?'
    
    def replace_content(match):
        included_file_name = match.group(1).strip()
        
        if not included_file_name.endswith('.tex'):
            included_file_name += '.tex'
        
        return get_paper_content(included_file_name, parent_dir_name)
    
    return re.sub(input_pattern, replace_content, content)