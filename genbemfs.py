import sys, os
import re
from bs4 import BeautifulSoup
from config import *
from logger import get_logger

__version__ = "0.0.1"

_html_blocks_dir = None
logger = get_logger()

def read_html_file(html_file_path):
    try:
        with open(html_file_path, 'r') as f:
            html_content = f.read()
    except FileNotFoundError:
        logger.warning(f'File {html_file_path} not found')
        sys.exit(1)
    return html_content

def html_to_bs(html_file_path):
    return BeautifulSoup(read_html_file(html_file_path), "html.parser")

def create_sub_dir(parent_dir, sub_dir):
    """
    Create sub directory if it doesn't exist
    """
    sub_dir_path = os.path.join(parent_dir, sub_dir)
    if not os.path.exists(sub_dir_path):
        os.makedirs(sub_dir_path)
    return sub_dir_path

def create_style_file(file_path, file_name):
    os.makedirs(file_path, exist_ok=True)
    html_file = os.path.join(file_path, f'{file_name}{CSS_FILE_EXT}')
 
    if not os.path.exists(html_file):
        with open(html_file, 'w') as f:
            f.write(f'.{file_name} {{\n    \n}}')

def create_block_file(block_name):
    block_dir = os.path.join(_html_blocks_dir, block_name)
    create_style_file(block_dir, block_name)

def create_elem_file(block_name, elem_name):
    block_dir = os.path.join(_html_blocks_dir, block_name, f'__{elem_name}')
    create_style_file(block_dir, f'{block_name}__{elem_name}')

def create_mod_file(block_name, elem_name, group=None):
    block_dir = os.path.join(_html_blocks_dir, block_name)
    group_name = f'_{group}' if group else ''
    elem_dir = os.path.join(block_dir, group_name, f'_{elem_name}' if not group else '')
    create_style_file(elem_dir, f'{block_name}{group_name}_{elem_name}')

def parse_html_files(html_src_file):
    bs = html_to_bs(html_src_file)
    for tag in bs.find_all():               # traverse all html tags
        class_attr = tag.get('class')
        if class_attr:
            for class_name in class_attr:
                re_block_elem = re.compile(r'^([a-zA-Z0-9-]+)__([a-zA-Z0-9-]+)$')
                re_block = re.compile(r'^([a-zA-Z0-9-]+)$')
                re_modifier = re.compile(r'^([a-zA-Z0-9-]+)_([a-zA-Z0-9-]+)$')
                re_modifier_with_group = re.compile(r'^([a-zA-Z0-9-]+)_([a-zA-Z0-9-]+)_([a-zA-Z0-9-]+)$')  # sample: button_theme_dark
                
                if re_block.match(class_name):
                    logger.info(f'Creating block {class_name}')
                    create_block_file(class_name)
                elif re_block_elem.match(class_name):
                    block_name = re_block_elem.match(class_name).group(1)
                    block_element = re_block_elem.match(class_name).group(2)
                    logger.info(f'Creating block {block_name} element {block_element}')
                    create_block_file(block_name)
                    create_elem_file(block_name, block_element)
                elif re_modifier.match(class_name):
                    block_name = re_modifier.match(class_name).group(1)
                    modifier = re_modifier.match(class_name).group(2)
                    logger.info(f'Creating block {block_name} modifier {modifier}')
                    create_block_file(block_name)
                    create_mod_file(block_name, modifier)
                elif re_modifier_with_group.match(class_name):
                    block_name = re_modifier_with_group.match(class_name).group(1)
                    group = re_modifier_with_group.match(class_name).group(2)
                    modifier = re_modifier_with_group.match(class_name).group(3)
                    logger.info(f'Creating block {block_name} modifier {modifier} in group {group}')
                    create_block_file(block_name)
                    create_mod_file(block_name, modifier, group=group)

def traverse_html_files_dir(html_dir):
    for file in os.listdir(html_dir):
        if file.endswith(HTML_FILE_EXT):
            file_path = os.path.join(html_dir, file)
            logger.info(f'Parsing {file_path}')
            parse_html_files(file_path)

def main():
    global _html_blocks_dir

    if len(sys.argv) < 2:
        print("Usage: python genbemfs.py <path to html files dir> [path to blocks dir]")
        print("Example: python genbemfs.py /path/to/html/files")
        sys.exit(1)

    if len(sys.argv) > 2:
        _html_blocks_dir = sys.argv[2]
    else:
        _html_blocks_dir = create_sub_dir(sys.argv[1], DEFAULT_BLOCKS_DIR)

    traverse_html_files_dir(sys.argv[1])

if __name__ == '__main__':
    main()