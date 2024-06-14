import os
from tqdm import tqdm


class Helper:
    def check_file(self, filename):
        return os.path.isfile(filename)

    def make_dir(self, name):
        if not os.path.isdir(name):
            os.makedirs(name)

    def download_file(self, url, local_path):
        import requests
        response = requests.get(url, stream=True)

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB

        with open(local_path, 'wb') as file, tqdm(
                desc="Downloading",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                miniters=1) as bar:
            for data in response.iter_content(block_size):
                bar.update(len(data))
                file.write(data)

        print("File downloaded successfully.\n")
