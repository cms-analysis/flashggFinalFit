import os
import io

def search_files_with_string(folder_path, search_string, exclude_extensions=('.root', '.pdf', '.png', '.pyc', '.o')):
    for root, dirs, files in os.walk(folder_path):
        if '.git' in dirs:
            dirs.remove('.git')
        for file_name in files:
            if (not file_name.endswith(exclude_extensions)) and ("cat" not in file_name) and ("ggtt_resonant_ggtt_resonant_mx" not in file_name and ("config_ggtt_batch_combined_mx" not in file_name)):
                file_path = os.path.join(root, file_name)
                try:
                    with io.open(file_path, 'r', encoding='utf-8') as file:
                        for line_number, line in enumerate(file, start=1):
                            if search_string in line:
                                print("Found in file: {}, line {}: {}".format(file_path, line_number, line.strip()))
                except UnicodeDecodeError as e:
                    print("Error reading {}: {}. Skipping this file.".format(file_path, e))
                    continue  # Skip this file
                except Exception as e:
                    print("Other error reading {}: {}. Skipping this file.".format(file_path, e))

# Usage example
folder_to_search = '.'
search_string = 'yagu'
search_files_with_string(folder_to_search, search_string)


