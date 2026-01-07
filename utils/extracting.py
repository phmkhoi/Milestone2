import re
import os
from utils.utils import find_root_file, get_paper_content
import bibtexparser
from bibtexparser.bparser import BibTexParser

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
        
        if not blocks:
            continue
        blocks = [b.strip() for b in blocks if b.strip()]
        if len(blocks) == 0: continue
        
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

    BLACK_LISTS = ['ref_camembert-bio.bib', 'anthology.bib']

    references = []
    for bib_file in bib_files:
        if bib_file in BLACK_LISTS:
            continue
        
        bib_path = os.path.join(dir_path, bib_file)
        
        if not os.path.isfile(bib_path):
            continue
        
        with open(bib_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            content = content
            
            parser = BibTexParser()
            parser.interpolate_strings = False
            
            refs_parsed = bibtexparser.loads(content, parser=parser)
            references.extend(refs_parsed.entries)

    return references


def deduplicate_references(results: list[str]) -> list[dict]:
    if not results:
        return []
    
    def get_key(value):
        return str(value).strip() if value else ''
    
    title_map = {}
    id_map = {}
    
    for obj in results[0]:
        title_key = get_key(obj.get('title'))
        id_key = get_key(obj.get('ID'))
        if title_key: title_map[title_key] = obj
        if id_key: id_map[id_key] = obj

    for i in range(1, len(results)):
        for j in range(len(results[i])):
            title_key = get_key(results[i][j].get('title'))
            id_key = get_key(results[i][j].get('ID'))

            if title_key in title_map:
                for key in results[i][j]:
                    if key not in title_map[title_key]:
                        title_map[title_key][key] = results[i][j][key]

            elif (title_key not in title_map and id_key in id_map):
                for key in results[i][j]:
                    if key not in id_map[id_key]:
                        id_map[id_key][key] = results[i][j][key]
            else:
                title_map[title_key] = results[i][j]
                
    return list(title_map.values())


def format_bib_string(entries: list[dict]) -> str:
    bib_entries = []
    
    ORDERS = ['author', 'title', 'booktitle', 'journal', 'publisher', 'year', 'volume', 'number', 'pages', 'howpublished']
    
    for fields in entries:
        entry_type = str(fields.get('ENTRYTYPE', 'misc'))
        entry_id = str(fields.get('ID', 'unknown'))
        
        entry_str = f"@{entry_type}{{{entry_id},\n"
        
        for k in ORDERS:
            if k in fields and fields[k]:
                value = str(fields[k])
                entry_str += f"  {k} = {{{value}}},\n"
        
        ignore_keys = set(ORDERS) | {'ID', 'ENTRYTYPE'}
        for k, v in fields.items():
            if k not in ignore_keys and v:
                 entry_str += f"  {k} = {{{str(v)}}},\n"
        
        entry_str += "}\n"
        bib_entries.append(entry_str)
        
    return '\n'.join(bib_entries)


def get_bib_objects(entries:list[dict], folder_path:str) -> dict:
    bib_entries = []
    
    for fields in entries:
        year_match = re.search(r'\d+', fields['year'])
        if year_match:
            year = year_match.group()
        else:
            year = 0
        
        temp_dict = {
            'cite_key': str(fields['ID']).lower(),
            'authors': str(fields['author']).lower().strip(),
            'title': str(fields['title']).lower().strip(),
            'year': int(year),
            'path': folder_path
        }
        
        bib_entries.append(temp_dict)
        
    return bib_entries


def get_references(folder_path:str, filter_list:list=None)->list[dict]:
    references = []
    tex_folder = os.path.join(folder_path, 'tex')
    
    if not os.path.isdir(tex_folder):
        return []
    
    if not os.listdir(tex_folder):
        return []
    
    for folder_version_path in os.listdir(tex_folder):
        full_path = os.path.join(tex_folder, folder_version_path)
        ref_dicts = read_bibs_in_dir(full_path)
        
        if ref_dicts is None:
            root_path = find_root_file(full_path)
            if not root_path:
                continue
            
            content = get_paper_content(root_path)
            ref_dicts = parse_bbl(content)
        
        if not ref_dicts:
            continue
        
        final_refs = []
        if filter_list:            
            for r in ref_dicts:
                if all(key in r for key in filter_list):
                    final_refs.append(r)
        else:
            final_refs = ref_dicts
            
        if final_refs:
            references.append(final_refs)
        
    return references


def save_bibs(folder_path:str)->None:
    references = get_references(folder_path)
    
    bib_path = os.path.join(folder_path, 'refs.bib')
    if os.path.isfile(bib_path):
        return
    
    if references:
        unique_data = deduplicate_references(references)
        bib_string = format_bib_string(unique_data)
        bib_path = os.path.join(folder_path, 'refs.bib')
        
        with open(bib_path, 'w', encoding='utf-8') as fw:
            fw.write(bib_string)
