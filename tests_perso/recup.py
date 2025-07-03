import os

def collect_py_files(root_dir, output_file):
    exclude_dirs = {'venv', 'env', '__pycache__'}

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for foldername, subfolders, filenames in os.walk(root_dir):
            # Exclure les dossiers indésirables
            subfolders[:] = [d for d in subfolders if d not in exclude_dirs]

            for filename in filenames:
                if filename.endswith('.py'):
                    filepath = os.path.join(foldername, filename)
                    outfile.write('#' * 80 + '\n')
                    outfile.write(f'# File: {filepath}\n')
                    outfile.write('#' * 80 + '\n\n')
                    try:
                        with open(filepath, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(content)
                            outfile.write('\n\n')
                    except Exception as e:
                        print(f"Could not read {filepath}: {e}")

if __name__ == '__main__':
    # Remplace ici par ton chemin de départ
    directory_to_scan = './'  # ou chemin absolu
    output_filename = 'all_python_files_combined.py'
    collect_py_files(directory_to_scan, output_filename)
    print(f'All .py files have been combined into {output_filename}')
