import re

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
    # entry_pattern = re.compile(r"\\bibitem\[.*?\]\{(.*?)\}([\s\S]*?)(?=\\bibitem|\\end\{thebibliography\})", re.MULTILINE)
    entry_pattern = re.compile(r"\\bibitem(?:\[.*?\])?\{(.*?)\}([\s\S]*?)(?=\\bibitem|\\end\{thebibliography\})", re.MULTILINE)
    bib_entries = []

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

        # source_match = re.search(r'(\{\\em\s+(.*?)\}|\\emph\{(.*?)\})', info_text)
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
        entry_type = "misc" 
        
        if "arxiv" in raw_body_flat.lower():
            entry_type = "misc"
            arxiv_match = re.search(r'(arXiv\s+preprint\s+arXiv:[0-9\.]+)', raw_body_flat, re.IGNORECASE)
            if arxiv_match:
                fields['howpublished'] = arxiv_match.group(1)
            else:
                fields['howpublished'] = "arXiv preprint"

        elif source_name:
            source_lower = source_name.lower()
            if re.search(r'(proceedings|symposium|conf\.|conference|workshop|focs|stoc|neurips|iclr|icml|aaai|acl|emnlp)', source_lower):
                entry_type = "inproceedings"
                fields['booktitle'] = source_name

            elif re.search(r'(press|publisher|sons|wiley|handbook)', source_lower):
                entry_type = "book"
                fields['publisher'] = source_name 

            else:
                entry_type = "article"
                fields['journal'] = source_name

        elif fields.get('pages'):
             entry_type = "article"
             remaining = clean_text(info_text)
             if remaining and len(remaining) > 3: 
                 fields['journal'] = remaining

        if key == "Mat":
            entry_type = "misc"
            fields['title'] = "Holy Bible, Matthew 1, 1--17"
            if 'author' in fields: del fields['author']

        # Tạo bibtex
        entry_str = f"@{entry_type}{{{key},\n"
        order = ['author', 'title', 'booktitle', 'journal', 'publisher', 'year', 'volume', 'number', 'pages', 'howpublished']
        
        for k in order:
            if k in fields and fields[k]:
                entry_str += f"  {k} = {{{fields[k]}}},\n"
        entry_str += "}\n"
        
        bib_entries.append(entry_str)

    return "\n".join(bib_entries)

def bbl2bib(bbl_input_path: str, bib_output_path: str):
    with open(bbl_input_path, "r", encoding="utf-8") as f:
        content = f.read()

    result = parse_bbl(content)

    with open(bib_output_path, "w", encoding="utf-8") as f:
        f.write(result)

if __name__ == "__main__":
    # Code nhận đầu vào là một file .bbl, sau đó tạo ra file .bib tương ứng đã chuẩn dạng bibtex
    bbl_input_file = "test.bbl"
    bib_output_file = "test_references.bib"

    # bbl_input_file = "main.bbl"
    # bib_output_file = "references.bib"
    
    bbl2bib(bbl_input_file, bib_output_file)
    print("done")