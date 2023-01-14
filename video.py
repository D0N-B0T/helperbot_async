import re
import requests
import urllib


class FileDownload:

    def __init__(self):
        pass

    def download_image(self, uri, folder, file_name, default_format=None):
        '''Downloads image to specified file name, preserving file type.'''
        if not uri:
            return None

        file_ext = self.find_file_format(uri, default_format=default_format)
        file_path = f"{folder}/{self._clean_name(file_name)}.{file_ext}"
        try:
            img_data = requests.get(uri).content
        except (ConnectionError, Exception) as e:
            print(f"--- {uri} caused error {e}")
            return None
        else:
            with open(file_path, "wb+") as f:
                f.write(img_data)
            print(f"Downloaded {file_path}")
            return f"{file_name}.{file_ext}"

    def download_video(self, uri, folder, file_name):
        '''Downloads video to specified file name, preserving file type.'''
        if not uri:
            return None

        file_ext = self.find_file_format(uri)
        file_path = f"{folder}/{self._clean_name(file_name)}.{file_ext}"
        try:
            urllib.request.urlretrieve(uri, file_path)
            print(f"Downloaded {file_path}")
        except Exception as e:
            print(f"--- {uri} caused error {e}")
            return None
        else:
            return f"{file_name}.{file_ext}"

    def find_file_format(self, uri, default_format=None):
        '''Extract file format of file to be downloaded.'''
        try:
            file_format = re.findall(r"(?<=\.)[a-z0-9]+(?=\?|$)", uri)[0]
        except IndexError:
            if default_format:
                file_format = default_format
            else:
                file_format = ""
        finally:
            return file_format

    def _clean_name(self, file_path):
        '''Ensure valid file name'''
        return re.sub("[&?=,']", "_", file_path)
    
    
