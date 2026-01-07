import os
import json
import Levenshtein
from tqdm import tqdm

from utils.extracting import get_references, deduplicate_references, get_bib_objects


def extract_references_to_objects(folder_path: str) -> list[dict]:
    '''
        folder_path: tex
    '''
    KEYS = ['ID', 'author', 'title', 'year']
    references = get_references(folder_path, filter_list=KEYS)
        
    if references:
        unique_data = deduplicate_references(references)
        result = get_bib_objects(unique_data, folder_path)
        return result
    
    return None


def convert_references_to_objects(folder_path: str) -> list[dict]:
    ref_path = os.path.join(folder_path, 'references.json')
    with open(ref_path, 'r', encoding='utf-8') as fr:
        ref_dict = json.load(fr)
        
    ref_list = []
    for key, value in ref_dict.items():
        temp_dict = {
            'arxiv_id': key.lower().strip(),
            'title': value['paper_title'].lower().strip(),
            'authors': ' and '.join(value['authors']).lower().strip(),
            'year': int(value['submission_date'][:4])
        }
        ref_list.append(temp_dict)
        
    return ref_list


def get_reference_objects(folder_path: str):
    extracted_refs = extract_references_to_objects(folder_path)
    converted_refs = convert_references_to_objects(folder_path)
    
    # extracted_path = os.path.join(folder_path, 'extracted.json')
    # converted_path = os.path.join(folder_path, 'converted.json')
    
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
                    arxiv_id = candidate['arxiv_id']
                    
        if best_ratio > 0:
            groundtruth_dicts[f'{item['cite_key']}'] = arxiv_id
            
    return groundtruth_dicts


def get_dataset(folder_path, threshold=0.9, nums=1500):
    dirs = os.listdir(folder_path)
    entries = []
    refs = []
    groundtruth_dict = {}
    cnt = 0
    cnt_dict = 0

    processing_bar = tqdm(total=nums, desc="Collecting Dataset")
    
    for dir in dirs:
        path = os.path.join(folder_path, dir)
        
        if not os.path.isfile(os.path.join(path, 'references.json')):
            continue
        
        converted_refs, extract_refs = get_reference_objects(path)
        
        if not extract_refs or not converted_refs:
            continue
        
        if len(converted_refs) < 20:
            continue
        
        entries.append(extract_refs)
        refs.append(converted_refs)
        
        temp_dict = get_ground_truth(converted_refs, extract_refs, threshold)
        if temp_dict:
            groundtruth_dict.update(temp_dict)
            
            # groundtruth_path = os.path.join(path, 'groundtruth.json')
            # with open(groundtruth_path, "w", encoding="utf-8") as f:
            #     json.dump(temp_dict, f, indent=4, ensure_ascii=False)
            cnt_dict += 1
            
        cnt += 1
        processing_bar.update(1)
        
        if cnt >= nums:
            break

    processing_bar.close()
    return entries, refs, groundtruth_dict


def get_manual_dataset(folder_path, paper_ids, groundtruth_dicts):
    entries = []
    refs = []
    groundtruth_dict = {}

    for i in range(len(paper_ids)):
        
        path = os.path.join(folder_path, paper_ids[i])
        
        if not os.path.isfile(os.path.join(path, 'references.json')):
            continue
        
        converted_refs, extract_refs = get_reference_objects(path)
        
        if not extract_refs or not converted_refs:
            continue
        
        entries.append(extract_refs)
        refs.append(converted_refs)
        
        groundtruth_dict.update(groundtruth_dicts[i])
        
        # groundtruth_path = os.path.join(path, 'groundtruth.json')
        # with open(groundtruth_path, "w", encoding="utf-8") as f:
        #     json.dump(groundtruth_dict, f, indent=4, ensure_ascii=False)
        
    return entries, refs, groundtruth_dict