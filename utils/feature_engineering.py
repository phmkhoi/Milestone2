import Levenshtein

def calculate_distance_similarity(s1: str, s2: str):
    return Levenshtein.ratio(s1, s2)

def convert_to_vector(entry: object, reference: object):
    title_entry = entry["title"]
    title_reference = reference["title"]
    author_entry = entry["authors"]
    author_reference = reference["authors"]
    year_entry = entry["year"]
    year_reference = reference["year"]
    title_distance = calculate_distance_similarity(title_entry, title_reference)
    author_entry = calculate_distance_similarity(author_entry, author_reference)

    year = 0
    if year_entry == year_reference:
        year = 1
    return [title_distance, author_entry, year]


def prepare_dataset(entry_array: list[list[object]], reference_array: list[list[object]], cite_to_arkiv: dict):
    vector_train = []
    ground_truth = []
    object_file = {}
    
    for i in range(len(entry_array)):
        file_path = None
        object_entry = {}
        
        for entry in entry_array[i]: 
            entry_name = entry['cite_key']
            entry_arr = []
            
            for reference in reference_array[i]:
                arxiv_id = reference['arxiv_id']
                vector = convert_to_vector(entry, reference)

                if file_path is None:
                    file_path = entry['path']
                    
                entry_arr.append({
                    "arxiv_id": arxiv_id,
                    "vector": vector
                })

                vector_train.append(vector)
                
                if entry['cite_key'] in cite_to_arkiv:
                    if cite_to_arkiv[entry['cite_key']] == reference['arxiv_id']:
                        ground_truth.append(1)
                    else:
                        ground_truth.append(0)
                else:
                    ground_truth.append(0)
                    
            object_entry[entry_name] = entry_arr
            
        object_file[file_path] = object_entry
        
    return vector_train, ground_truth, object_file