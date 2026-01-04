from utils.parser import parse_paper
from utils.bbl2bib import bbl2bib
from tqdm import tqdm
import os

def main_function(folder_path):
    dirs = os.listdir(folder_path)

    for dir in tqdm(dirs):
        path = os.path.join(folder_path, dir)
        
        tex_folder = path + '/tex/'
        
        bbl2bib(tex_folder)
        # parse_paper(tex_folder)
        
if __name__ == "__main__":
    folder_path = './MockFolder/'
    main_function(folder_path)