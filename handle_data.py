# import pandas as pd
# df = pd.read_parquet('project_1/train-00000-of-00001.parquet', engine='pyarrow')
# print(df.head())


# 10000text to 1 text
import os
import shutil

# Đường dẫn đến thư mục chứa các file văn bản
folder_path = 'project_1/10000_books/output'

output_file = 'output.txt'
file_count = 0

with open(output_file, 'wb') as outfile:
    # Duyệt qua tất cả các file trong thư mục
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith('.txt'):
            with open(file_path, 'rb') as infile:
                # Sao chép nội dung từ file đầu vào vào file đầu ra mà không tải toàn bộ vào bộ nhớ
                shutil.copyfileobj(infile, outfile)
                outfile.write(b'\n')
            file_count += 1

        print(f'Đã ghép {file_count} file vào {output_file}')

