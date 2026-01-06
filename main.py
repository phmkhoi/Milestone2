from tqdm import tqdm
import os
import logging
from sklearn.utils import shuffle

from utils.parsing import parse_paper
from utils.dataset import get_dataset, get_manual_dataset
from utils.extracting import save_bibs
from utils.utils import remove_tex_folder
from utils.manual import MANUAL_ID, GROUNDTRUTHS
from utils.feature_engineering import prepare_dataset
from models.model import Model
from config import RETURN_TREE, THRESHOLD, NUM_PAPERS_USING_TOOL, NUM_EPOCHS, FOLDER_PATH

def process_matching(folder_path:str):
    tool_entries, tool_refs, tool_groundtruth = get_dataset(folder_path, threshold=THRESHOLD, nums=NUM_PAPERS_USING_TOOL)
    manual_entries, manual_refs, manual_groundtruth = get_manual_dataset(folder_path, MANUAL_ID, GROUNDTRUTHS)
    
    tool_entries, tool_refs = shuffle(tool_entries, tool_refs, random_state=0)
    
    if manual_entries:
        manual_entries, manual_refs = shuffle(manual_entries, manual_refs, random_state=0)
        
        groundtruth = tool_groundtruth.copy()
        groundtruth.update(manual_groundtruth)
        
        entries_test = manual_entries[0:1] + tool_entries[0:1]
        refs_test = manual_refs[0:1] + tool_refs[0:1]
        
        entries_valid = manual_entries[1:2] + tool_entries[1:2]
        refs_valid = manual_refs[1:2] + tool_refs[1:2]
        
        entries_train = manual_entries[2:] + tool_entries[2:]
        refs_train = manual_refs[2:] + tool_refs[2:]
        
    else:
        groundtruth = tool_groundtruth.copy()
        
        entries_test = tool_entries[0:1]
        refs_test = tool_refs[0:1]
        
        entries_valid = tool_entries[1:2]
        refs_valid = tool_refs[1:2]
        
        entries_train = tool_entries[2:]
        refs_train = tool_refs[2:]
    
    print('=' * 99)
    print(f'Number of Train\'s Papers = {len(entries_train)}')
    print(f'Number of Valid\'s Papers = {len(entries_valid)}')
    print(f'Number of Test\'s Papers = {len(entries_test)}')
    
    vector_train, ground_truth_train, object_train = prepare_dataset(entries_train, refs_train, groundtruth)
    vector_valid, ground_truth_valid, object_valid = prepare_dataset(entries_valid, refs_valid, groundtruth)
    vector_test, ground_truth_test, object_test = prepare_dataset(entries_test, refs_test, groundtruth)
    
    model = Model()
    model.train(vector_train, ground_truth_train, vector_valid, ground_truth_valid, num_epoch=NUM_EPOCHS)
    model.predict_top_k(object_train, 5, groundtruth, 'train')
    model.predict_top_k(object_valid, 5, groundtruth, 'valid')
    model.predict_top_k(object_test, 5, groundtruth, 'test', return_object=True)

def main_function(folder_path:str):
    logger = logging.getLogger('bibtexparser')
    logger.setLevel(logging.ERROR)
    
    dirs = os.listdir(folder_path)

    for dir in tqdm(dirs, desc='Processing Papers'):
        path = os.path.join(folder_path, dir)
        parse_paper(path, return_tree=RETURN_TREE)
        save_bibs(path)
        
    process_matching(folder_path)
    remove_tex_folder(folder_path)

    
if __name__ == "__main__":
    main_function(FOLDER_PATH)