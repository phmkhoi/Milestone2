from utils.parser import parse_paper
import os

folder_path = './MockFolder/'

dirs = os.listdir(folder_path)

for dir in dirs:
    path = os.path.join(folder_path, dir)
    parse_paper(path)