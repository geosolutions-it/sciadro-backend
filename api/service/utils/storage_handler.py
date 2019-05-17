import errno
import os
import zipfile
import shutil
from abc import ABC, abstractmethod

from service.utils.exception import FileManagementException


class AStorageManager(ABC):
    telem_ext = 'telem'
    video_ext = 'avi'
    frame_ext = 'xml'

    def __init__(self, file_name, file_path):
        self.file_name = file_name.split('.')[0]
        self.file_path = file_path
        self.temp_dir_path = file_path.split('.')[0]

    @abstractmethod
    def save_temporary_file(self, file):
        pass

    def unzip_file(self):
        self.create_directory()
        zip_ref = zipfile.ZipFile(self.file_path, 'r')
        zip_ref.extractall(self.temp_dir_path)

    @abstractmethod
    def create_directory(self):
        pass

    @abstractmethod
    def delete_temporary_files(self):
        pass

    @abstractmethod
    def get_telem_file(self):
        pass

    @abstractmethod
    def get_video_file(self):
        pass

    @abstractmethod
    def get_xml_file(self):
        pass


class SystemFileStorage(AStorageManager):

    def get_telem_file(self):
        file_path = f'{os.path.join(self.temp_dir_path, self.file_name)}.{self.telem_ext}'
        return open(file_path, 'rb')

    def get_video_file(self):
        file_path = f'{os.path.join(self.temp_dir_path, self.file_name)}.{self.video_ext}'
        return open(file_path, 'rb')

    def get_xml_file(self):
        file_path = f'{os.path.join(self.temp_dir_path, self.file_name)}.{self.frame_ext}'
        return open(file_path, 'r')

    def create_directory(self):
        if not os.path.exists(os.path.dirname(self.file_path)):
            try:
                os.makedirs(os.path.dirname(self.file_path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise FileManagementException(f'Error during managing temporary files {exc}')

    def delete_temporary_files(self):
        to_remove = os.path.abspath(os.path.join(self.temp_dir_path, os.pardir))
        shutil.rmtree(to_remove)

    def save_temporary_file(self, file):
        self.create_directory()
        with open(self.file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
