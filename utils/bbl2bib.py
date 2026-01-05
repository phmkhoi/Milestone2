import re
import os
from utils.utils import find_root_file, get_paper_content
import bibtexparser
import json
import Levenshtein

def clean_text(text):
    if not text: return ""

    text = text.replace('\n', ' ').replace('\r', ' ').replace('~', ' ')

    text = re.sub(r'\\newblock', '', text)
    text = re.sub(r'\\em\b', '', text) 
    text = re.sub(r'\\emph', '', text)
    text = re.sub(r'\{\\etalchar\{.*?\}\}', '', text)
    text = re.sub(r'^\s*In\s+', '', text, flags=re.IGNORECASE) 

    text = text.strip(' .,;:')

    while (text.startswith('{') and text.endswith('}')) or \
          (text.startswith('(') and text.endswith(')')):
        if len(text) > 2:
            text = text[1:-1].strip()
        else:
            break

    text = text.strip(' .,;:')
    text = text.lower()
    return re.sub(r'\s+', ' ', text).strip()
 
 
def format_authors(text):
    if not text: return ""
    text = clean_text(text)
    text = re.sub(r',?\s+et\s+al\.?', ' and others', text, flags=re.IGNORECASE)
    text = text.replace(', ', ' and ')
    text = re.sub(r'\s+and\s+and\s+', ' and ', text)
    return text


def parse_bbl(bbl_content):
    entry_pattern = re.compile(r"\\bibitem(?:\[.*?\])?\{(.*?)\}([\s\S]*?)(?=\\bibitem|\\end\{thebibliography\})", re.MULTILINE)
    bib_references = []

    for match in entry_pattern.finditer(bbl_content):
        key = match.group(1).strip()
        raw_body = match.group(2).strip()
        
        raw_body_flat = raw_body.replace('\n', ' ').replace('\r', ' ')
        blocks = re.split(r'\\newblock', raw_body_flat)
        blocks = [b.strip() for b in blocks if b.strip()]
        
        fields = {}
        info_text = ""
        
        # Tách Author - Title - Info
        if len(blocks) >= 2:
            fields['author'] = format_authors(blocks[0])
            fields['title'] = clean_text(blocks[1])
            info_text = " ".join(blocks[2:]) if len(blocks) > 2 else ""
        else:
            fields['title'] = clean_text(blocks[0])
            info_text = blocks[0]

        source_match = re.search(r'(\{\\em\s+((?:[^{}]|\{.*?\})*)\}|\\emph\{((?:[^{}]|\{.*?\})*)\})', info_text)
        
        source_name = ""
        if source_match:
            raw_source = source_match.group(2) if source_match.group(2) else source_match.group(3)
            source_name = clean_text(raw_source)
            info_text = info_text.replace(source_match.group(0), '')
        
        # Year
        year_match = re.search(r'\b(19|20)\d{2}\b(?=[^0-9]*$)', info_text)
        if not year_match:
            year_match = re.search(r'\b(19|20)\d{2}\b', info_text)
        if year_match:
            fields['year'] = year_match.group(0)
            info_text = info_text[:year_match.start()] + info_text[year_match.end():]

        # Pages
        pages_match = re.search(r'pages\s+([0-9\-]+)', info_text)
        if not pages_match:
            pages_match = re.search(r':\s*([0-9]+--[0-9]+)', info_text)
        if pages_match:
            fields['pages'] = pages_match.group(1)
            info_text = info_text.replace(pages_match.group(0), '')

        # Publisher
        if "IEEE" in info_text: fields['publisher'] = "IEEE"
        elif "Springer" in info_text: fields['publisher'] = "Springer"
        elif "ACM" in info_text: fields['publisher'] = "ACM"
        elif "Addison-Wesley" in info_text: fields['publisher'] = "Addison-Wesley"
        elif "Cambridge" in info_text: fields['publisher'] = "Cambridge University Press"

        # PHÂN LOẠI (book/article/misc/proceedings)
        ENTRYTYPE = "misc" 
        
        if "arxiv" in raw_body_flat.lower():
            ENTRYTYPE = "misc"
            arxiv_match = re.search(r'(arXiv\s+preprint\s+arXiv:[0-9\.]+)', raw_body_flat, re.IGNORECASE)
            if arxiv_match:
                fields['howpublished'] = arxiv_match.group(1)
            else:
                fields['howpublished'] = "arXiv preprint"

        elif source_name:
            source_lower = source_name.lower()
            if re.search(r'(proceedings|symposium|conf\.|conference|workshop|focs|stoc|neurips|iclr|icml|aaai|acl|emnlp)', source_lower):
                ENTRYTYPE = "inproceedings"
                fields['booktitle'] = source_name

            elif re.search(r'(press|publisher|sons|wiley|handbook)', source_lower):
                ENTRYTYPE = "book"
                fields['publisher'] = source_name 

            else:
                ENTRYTYPE = "article"
                fields['journal'] = source_name

        elif fields.get('pages'):
             ENTRYTYPE = "article"
             remaining = clean_text(info_text)
             if remaining and len(remaining) > 3: 
                 fields['journal'] = remaining

        if key == "Mat":
            ENTRYTYPE = "misc"
            fields['title'] = "Holy Bible, Matthew 1, 1--17"
            if 'author' in fields: del fields['author']

        fields['ENTRYTYPE'] = ENTRYTYPE
        fields['ID'] = key
        bib_references.append(fields)
    return bib_references


def read_bibs_in_dir(dir_path: str):
    if not os.path.isdir(dir_path):
        return None
    bib_files = [f for f in os.listdir(dir_path) if f.endswith(".bib")]

    if not bib_files:
        return None

    references = []
    for bib_file in bib_files:
        bib_path = os.path.join(dir_path, bib_file)
        with open(bib_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            content = content.replace('cvpr', '{cvpr}')
            
            refs_parsed = bibtexparser.loads(content)
            references.extend(refs_parsed.entries)

    return references


def deduplicate_reference(results: list[str]) -> str:
    # title_map = {}
    # ID_map = {}
    # keys = ['ID', 'author', 'title', 'year']
    
    # for obj in results[0]:
    #     valid = True
    #     for key in keys:
    #         if key not in obj.keys():
    #             valid = False
    #             break
            
    #     if valid:
    #         title_map.update({obj['title']: obj})
    #         ID_map.update({obj['ID']: obj})
    # for i in range(1, len(results)):
    #     for j in range(len(results[i])):
    #         keys = ['ID', 'author', 'title', 'year']
    #         for k in keys:
    #             if k not in results[i][j].keys():
    #                 results[i].remove(results[i][j])
    #                 break
    title_map = {obj['title']: obj for obj in results[0]}
    ID_map = {obj['ID']: obj for obj in results[0]}
        
    for i in range(1, len(results)):
        for j in range(len(results[i])):
            title = results[i][j]['title']
            ID = results[i][j]['ID']
            #Title trùng thì chắc chắn đúng.
            if title in title_map:
                for key in results[i][j]:
                    #Check xem liệu trong result_map có trường nào không có key không. Nếu như có thì bổ sung
                    if key not in title_map[title]:
                        title_map[title][key] = results[i][j][key]
            #Nếu title không trùng thì xét tiếp ID
            elif (title not in title_map and ID in ID_map):
                for key in results[i][j]:
                    #Check xem liệu trong result_map có trường nào không có key không. Nếu như có thì bổ sung
                    if key not in ID_map[ID]:
                        ID_map[ID][key] = results[i][j][key]
            else:
                title_map[title] = results[i][j]
    
    bib_entries = []
    keys = ['ID', 'author', 'title', 'year']
    for fields in title_map.values():
        valid = True
        for key in keys:
            if key not in fields.keys():
                valid = False
                break
        
        if not valid:
            continue
        
        year_match = re.search(r'\d+', fields['year'])
        if year_match:
            year = year_match.group()
        else:
            year = 0
        
        temp_dict = {
            'cite-key': fields['ID'].lower(),
            'authors': fields['author'].lower().strip(),
            'title': fields['title'].lower().strip(),
            'year': int(year)
        }
        
        bib_entries.append(temp_dict)
    return bib_entries


def extract_references(folder_path: str) -> None:
    '''
        folder_path: tex
    '''
    references = []
    
    tex_folder = folder_path + '/tex/'
    
    if not os.path.isdir(tex_folder): return None
    if not os.listdir(tex_folder): return None

    for folder_version_path in os.listdir(tex_folder):
        full_path = tex_folder + folder_version_path
        
        ref_dicts = read_bibs_in_dir(full_path)
        if ref_dicts is None:
            root_path = find_root_file(full_path)
            content = get_paper_content(root_path)
            ref_dicts = parse_bbl(content)
        
        ref_dicts_valid = []
        for r in ref_dicts:
            keys = ['ID', 'author', 'title', 'year']
            valid = True
            for key in keys:
                if key not in r.keys(): 
                    valid = False
                    ref_dicts.remove(r)
                    break
            if valid: ref_dicts_valid.append(r)
                    
        references.append(ref_dicts_valid)
    if references:
        # print(references)
        result = deduplicate_reference(references)
            
    return result

def convert_references_to_objects(folder_path: str):
    ref_path = os.path.join(folder_path, 'references.json')
    with open(ref_path, 'r', encoding='utf-8') as fr:
        ref_dict = json.load(fr)
        
    ref_list = []
    for key, value in ref_dict.items():
        temp_dict = {
            'arxiv-id': key.lower().strip(),
            'title': value['paper_title'].lower().strip(),
            'authors': ' and '.join(value['authors']).lower().strip(),
            'year': int(value['submission_date'][:4])
        }
        ref_list.append(temp_dict)
        
    return ref_list

def get_reference_objects(folder_path: str):
    extracted_refs = extract_references(folder_path)
    converted_refs = convert_references_to_objects(folder_path)
    
    # if extracted_refs and converted_refs:
    #     extracted_path = os.path.join(folder_path, 'extracted.json')
    #     converted_path = os.path.join(folder_path, 'converted.json')
        
        # with open(extracted_path, "w", encoding="utf-8") as f:
        #     json.dump(extracted_refs, f, indent=4, ensure_ascii=False)
            
        # with open(converted_path, "w", encoding="utf-8") as f:
        #     json.dump(converted_refs, f, indent=4, ensure_ascii=False)
        
    return converted_refs, extracted_refs

def get_ground_truth(converted_refs, extract_refs, threshold):
    groundtruth_dicts = {}
    
    if not (converted_refs and extract_refs):
        return None
    
    for item in extract_refs:
        best_ratio = 0
        arxiv_id = None
        
        for candidate in converted_refs:
            ratio = Levenshtein.ratio(item['title'], candidate['title'])
            if ratio >= threshold:
                if ratio > best_ratio:
                    best_ratio = ratio
                    arxiv_id = candidate['arxiv-id']
                    
        if best_ratio > 0:
            groundtruth_dicts[f'{item['cite-key']}'] = arxiv_id
            
    return groundtruth_dicts
    
def get_dataset(folder_path, threshold=0.9, nums=1500):
    dirs = os.listdir(folder_path)
    entries = []
    refs = []
    groundtruth_dict = {}
    cnt = 0
    cnt_dict = 0

    for dir in (dirs):
        path = os.path.join(folder_path, dir)
    
        if not os.path.isfile(os.path.join(path, 'references.json')):
            # print(f'[ERROR][prepare_dataset]: {os.path.join(path, 'references.json')} Not Existed')
            continue
        
        converted_refs, extract_refs = get_reference_objects(path)
        
        if not extract_refs or not converted_refs:
            continue
        
        entries.append(extract_refs)
        refs.append(converted_refs)
        
        temp_dict = get_ground_truth(converted_refs, extract_refs, threshold)
        if temp_dict:
            groundtruth_dict.update(temp_dict)
            
            groundtruth_path = os.path.join(path, 'groundtruth.json')
            with open(groundtruth_path, "w", encoding="utf-8") as f:
                json.dump(temp_dict, f, indent=4, ensure_ascii=False)
            cnt_dict += 1
            
        cnt += 1
        if cnt >= nums:
            break
        
    print(f'Number of appending dicts: {cnt_dict}')
    return entries, refs, groundtruth_dict