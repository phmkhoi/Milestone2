from utils.parser import parse_paper
from utils.bbl2bib import get_dataset
from tqdm import tqdm
import os


def main_function(folder_path):
    dirs = os.listdir(folder_path)

    # for dir in tqdm(dirs):
    #     path = os.path.join(folder_path, dir)
    #     parse_paper(path)
        
    tool_entries, tool_refs, tool_groundtruth = get_dataset(folder_path, threshold=0.8, nums=50)
    print(f'Entries = {len(tool_entries)}')
    print(f'Refs = {len(tool_refs)}')
    print(f'Groundtruth = {len(tool_groundtruth.keys())}')
        
if __name__ == "__main__":
    folder_path = './MockFolder/'
    main_function(folder_path)