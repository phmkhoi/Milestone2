from utils.parser import parse_paper
from utils.bbl2bib import get_dataset, extract_references
from tqdm import tqdm
import os
from utils.feature_engineering import khong_biet_dat_ten_gi
from models.model import Model
import logging
def main_function(folder_path):
    logger = logging.getLogger('bibtexparser')
    logger.setLevel(logging.ERROR)
    dirs = os.listdir(folder_path)

    # for dir in tqdm(dirs):
    #     path = os.path.join(folder_path, dir)
    #     parse_paper(path)
        
    entries, refs, tool_groundtruth = get_dataset(folder_path, threshold=0.8, nums=1500)
    entries_train = entries[:-4]
    refs_train = refs[:-4]
    entries_valid = entries[-4:-2]
    refs_valid = refs[-4:-2]
    entries_test = entries[-2:]
    refs_test = refs[-2:]
    
    for entry in entries_valid:
        print(entry)
        
    for entry in entries_test:
        print(entry)
    
    print(f'Groundtruth = {len(tool_groundtruth.keys())}')
    print(f'Train Entries = {len(entries_train)}')
    print(f'Train Refs = {len(refs_train)}')
    print(f'Test Entries = {len(entries_test)}')
    print(f'Test Refs = {len(refs_test)}')
    
    vector_train, ground_truth_train, nothing_train = khong_biet_dat_ten_gi(entries_train, refs_train, tool_groundtruth)
    vector_valid, ground_truth_valid, nothing_valid = khong_biet_dat_ten_gi(entries_valid, refs_valid, tool_groundtruth)
    vector_test, ground_truth_test, nothing_test = khong_biet_dat_ten_gi(entries_test, refs_test, tool_groundtruth)
    
    model = Model()
    model.train(vector_train, ground_truth_train, vector_valid, ground_truth_valid, num_epoch=1)
    model.predict_top_k(nothing_train, 5, tool_groundtruth, 'train')
    model.predict_top_k(nothing_valid, 5, tool_groundtruth, 'valid')
    model.predict_top_k(nothing_test, 5, tool_groundtruth, 'test', return_object=True)
if __name__ == "__main__":
    folder_path = './23127072/'
    main_function(folder_path)
    # result = extract_references('/23127072/2306-16226')