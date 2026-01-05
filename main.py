from utils.parser import parse_paper
from utils.bbl2bib import get_dataset
from tqdm import tqdm
import os

def main_function(folder_path):
    # dirs = os.listdir(folder_path)

    # for dir in tqdm(dirs):
    #     path = os.path.join(folder_path, dir)
        
    #     tex_folder = path + '/tex/'
        
        
    #     # parse_paper(tex_folder)
        
    entries, refs, groundtruth = get_dataset(folder_path, threshold=0.7, nums=50)
    print(f'Entries = {len(entries)}')
    print(f'Refs = {len(refs)}')
    print(f'Groundtruth = {len(groundtruth.keys())}')
        
if __name__ == "__main__":
    folder_path = './23127072/'
    main_function(folder_path)