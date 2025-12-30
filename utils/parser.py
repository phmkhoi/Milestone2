import re
import os
import json
    
from models.hierarchy_tree import HierarchyTree, Node
from models.hierarchy_manager import HierarchyManager
from utils.processing import normalize_equation


BLOCK_PATTERN = re.compile(r'\\(begin|end){([^}]+)\*?\}')


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


def add_sentences_to_tree(paragraph, tree):
    if not paragraph:
        return
    
    if isinstance(paragraph, list):
        paragraph = ' '.join(paragraph)
    
    abbreviations = [
        (r'et al\.', 'et al_'), 
        (r'i\.e\.', 'i_e_'), 
        (r'e\.g\.', 'e_g_'), 
        (r'Fig\.', 'Fig_'),
        (r'Eq\.', 'Eq_'),
        (r'Tab\.', 'Tab_'),
        (r'Avg\.', 'Avg_')
    ]
    
    for pattern, place_holder in abbreviations:
        paragraph = re.sub(pattern, place_holder, paragraph, flags=re.IGNORECASE)
    
    split_pattern = r'(?<=[.!?])\s+'
    
    sentences = re.split(split_pattern, paragraph)

    for sentence in sentences:
        
        for pattern, place_holder in abbreviations:
            original_str = pattern.replace('\\', '')
            sentence = sentence.strip().replace(place_holder, original_str)
        
        current_node = Node(sentence)
        tree.add_node(current_node, 'leaf')
        
        
def add_block_to_tree(content_list, tree):
    first_line = content_list[0]
    match = BLOCK_PATTERN.search(first_line)
    LEAF_BLOCKS = ['equation', 'figure']
    
    tag = match.group(2)
    
    if tag in LEAF_BLOCKS:
        content = ' '.join(content_list).replace('\n', ' ')
        current_node = Node(content)
        tree.add_node(current_node, 'leaf')
        return
        
    container_node = Node(tag.capitalize())
    tree.add_node(container_node)
    
    inner_block = content_list[1:-1]
    parse_inner_block(inner_block, tree)
    
    tree.step_out()
    
def parse_inner_block(lines, tree):
    i = 0
    buffer = []
    
    while i < len(lines):
        line = lines[i].strip()
          
        match = BLOCK_PATTERN.search(line)
        
        if match and match.group(1) == 'begin':
            add_sentences_to_tree(buffer, tree)
            buffer.clear()
            
            tag = match.group(2)
            end_idx = find_end_position(lines, i, tag)
            
            if end_idx != -1:
                sub_block = lines[i:end_idx + 1]
                add_block_to_tree(sub_block, tree)
                
                i = end_idx + 1
                continue
            
        if lines:
            buffer.append(line)
            
        i += 1
        
    add_sentences_to_tree(buffer, tree)

def find_end_position(lines, start_idx, given_tag):
    
    depth = 0
    
    for j in range(start_idx, len(lines)):
        match = BLOCK_PATTERN.search(lines[j])
        
        if match:
            action, tag = match.groups()
            
            if tag == given_tag:
                if action == 'begin':
                    depth += 1
                elif action == 'end':
                    depth -= 1
        
                if depth == 0:
                    return j
    return -1

def convert_paper_to_tree(raw_content):
    main_content = get_document_body(raw_content)
    
    lines = main_content.split('\n')

    section_pattern = re.compile(r'\\(part|chapter|section|subsection|subsubsection)\s*\{([^}]*)\}')
    
    block_content = []
    block_tag = None
    denied_tag = ['comment', 'thebibliography']
    
    bracket = 0
    bracket_content = []
    is_inside_bracket = False
    
    tree = HierarchyTree()
    
    for line in lines:
        line = line.strip().replace('\n', '')

        section_match = section_pattern.search(line)
        if section_match:
            type = section_match.group(1)
            node_content = section_match.group(2)
            
            current_node = Node(node_content)
            tree.add_node(current_node, type)
            
            continue
        
        
        block_match = BLOCK_PATTERN.search(line)
        
        if block_tag:
            block_content.append(line)
            
            if block_match:
                action, tag = block_match.groups()
                if action == 'end' and tag == block_tag:
                    if not (tag in denied_tag):
                        add_block_to_tree(block_content, tree)
                        
                    block_content = []
                    block_tag = None
                    
            continue
        
        if block_match:
            action, tag = block_match.groups()
            if action == 'begin':
                block_tag = tag
                block_content.append(line)
                
            continue
        
        if '{' in line:
            is_inside_bracket = True
        
        bracket += line.count('{')
        bracket -= line.count('}')       
            
        if is_inside_bracket:
            bracket_content.append(line)
            
            if bracket == 0:
                if bracket_content:
                    add_sentences_to_tree(bracket_content, tree)
                    
                bracket_content.clear()
                is_inside_bracket = False
                
            continue
            
        if line.startswith('%') or line.startswith('\\') or line == '':
            continue

        add_sentences_to_tree(line, tree)
        
    return tree
       

def convert_tree_to_dict(tree, manager):
    hierarchy_dict = {}
    
    stack = [(tree.root, None)]
    
    while stack:
        node, parent_id = stack.pop()
        
        node_id = manager.get_id(node.content)
        
        if parent_id is not None:
            hierarchy_dict[node_id] = parent_id
            
        for child in reversed(node.children):
            stack.append((child, node_id))
            
    return hierarchy_dict


def get_hierarchy_structure(version_trees):
    manager = HierarchyManager()
    hierarchy_dict = {}
    
    for version_idx, tree in version_trees.items():
        hierarchy_dict[version_idx] = convert_tree_to_dict(tree, manager)
        
    result_dict = {
        'elements': manager.output,
        'hierarchy': hierarchy_dict
    }
    
    return result_dict

def clean_tex(raw_content):
    content = normalize_equation(raw_content)
    
    REPLACES = [r'\\label\s*\{([^}]+)\}', 
                r'\\quad', r'\\noindent', 
                r'\\item', r'\\\\',
                r'\\smallskip',
                r'\\centuring']
    
    for replace in REPLACES:
        content = re.sub(replace, '', content)
        
    return content
    

def parse_paper(folder_path):
    tex_folder = folder_path + '/tex/'
    version_folders = os.listdir(tex_folder)
    
    if not version_folders:
        return
    
    versions = {}
    
    for idx, folder in enumerate(version_folders):
        full_path = tex_folder + folder
        
        root_path = find_root_file(full_path)
        content = get_paper_content(root_path)
        
        cleaned_content = clean_tex(content)
        # with open ('./after.tex', 'w', encoding='utf-8') as fr:
        #     fr.write(cleaned_content)
        
        tree = convert_paper_to_tree(cleaned_content)
        
        # with open(f'./tree{idx + 1}.txt', 'w') as fr:
        #     fr.write(tree.to_string())

        versions[f'{idx + 1}'] = tree

    result_dict = get_hierarchy_structure(versions)
    output_path = os.path.join(folder_path, os.path.dirname(tex_folder).split('/')[-2] + '.json')

    with open(output_path, 'w') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=4)