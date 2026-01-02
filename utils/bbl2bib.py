import re
import os
from utils.utils import find_root_file, get_paper_content
import bibtexparser

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
    return re.sub(r'\s+', ' ', text).strip()
 
def format_authors(text):
    if not text: return ""
    text = clean_text(text)
    text = re.sub(r',?\s+et\s+al\.?', ' and others', text, flags=re.IGNORECASE)
    text = text.replace(', ', ' and ')
    text = re.sub(r'\s+and\s+and\s+', ' and ', text)
    return text

def parse_bbl(bbl_content):
    entry_pattern = re.compile(
        r"\\bibitem(?:\[[^\]]*\])?\{(.*?)\}([\s\S]*?)(?=\\bibitem|\\end\{thebibliography\})",
        re.MULTILINE
    )    
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

# def bbl2bib(bbl_input_path: str, bib_output_path: str):
#     with open(bbl_input_path, "r", encoding="utf-8") as f:
#         content = f.read()

#     result = parse_bbl(content)
#     return result

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
            refs_parsed = bibtexparser.loads(f.read())
            references.extend(refs_parsed.entries)

    return references

def bbl2bib(folder_path: str, bib_output_folder: str) -> None:
    '''
        folder_path: tex
    '''
    references = []
    if not os.path.isdir(folder_path): return None

    for folder_version_path in os.listdir(folder_path):
        #Do t dùng macbook nên cần...
        # if folder_version_path == ".DS_Store":
        #     continue
        # with open(os.path.join(folder_path,folder_version_path, 'ms.tex'), "r", encoding="utf-8") as f:
        #     content = f.read()
        full_path = folder_path + folder_version_path
        
        # 2 dòng này dùng để lấy content của file tex, không phải lấy file bib
        # Hướng xử lí: dò theo file bib nếu paper có đính kèm
        ref_dicts = read_bibs_in_dir(full_path)
        if ref_dicts is None:
            root_path = find_root_file(full_path)
            content = get_paper_content(root_path)
            ref_dicts.extend(parse_bbl(content))
        
        references.append(ref_dicts)
    result = deduplicate_reference(references)
    
    output_path = os.path.join(bib_output_folder, os.path.dirname(folder_path).split('/')[-2] + '.bib')
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)
        print(f"Write refs in {output_path}")

def deduplicate_reference(results: list[str]) -> str:
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
    for fields in title_map.values():
        entry_str = f"@{fields['ENTRYTYPE']}{{{fields['ID']},\n"
        order = ['author', 'title', 'booktitle', 'journal', 'publisher', 'year', 'volume', 'number', 'pages', 'howpublished']
        
        for k in order:
            if k in fields and fields[k]:
                entry_str += f"  {k} = {{{fields[k]}}},\n"
        entry_str += "}\n"
        bib_entries.append(entry_str)
    return "\n".join(bib_entries)

# if __name__ == "__main__":
#     bib_output_file = "references.bib"
    
#     # bbl2bib(bbl_input_file, bib_output_file)

#     #Truyền vào folder gốc
#     bbl2bib("1706-03762/tex", bib_output_file)