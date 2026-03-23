import os
import shutil

install_dir = r'C:\Kratos_IGA_RM\Kratos\bin\Release\KratosMultiphysics'

for root, dirs, files in os.walk(install_dir):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                first_line = f.readline().strip()
            if first_line.startswith('C:\\') or first_line.startswith('C:/'):
                source_path = first_line.replace('\\', os.sep).replace('/', os.sep)
                if os.path.exists(source_path):
                    shutil.copy(source_path, file_path)
                    print(f'Fixed: {file_path} (copied from {source_path})')
                else:
                    print(f'Warning: Source not found for {file_path} - {source_path}')