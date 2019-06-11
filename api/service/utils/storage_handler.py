import errno
import os
import zipfile
import shutil
from abc import ABC, abstractmethod
from os import listdir
from os.path import isfile

from service.utils.exception import FileManagementException


class AStorageManager(ABC):
    telem_ext = 'telem'
    video_ext = 'avi'
    frame_ext = 'xml'

    def __init__(self, file_name, file_path):
        self.file_name = file_name.split('.')[0]
        self.file_path = file_path
        self.temp_dir_path = file_path.split('.')[0] + 'temp'

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
        return open(self.find_file_by_ext(self.telem_ext), 'rb')

    def get_video_file(self):
        return open(self.find_file_by_ext(self.video_ext), 'rb')

    def get_xml_file(self):
        return open(self.find_file_by_ext(self.frame_ext), 'r')

    def find_file_by_ext(self, file_ext):
        zip_files = [f for f in listdir(self.temp_dir_path) if isfile(os.path.join(self.temp_dir_path, f))]
        for file in zip_files:
            if file_ext in file:
                file_path = f'{os.path.join(self.temp_dir_path, file)}'
                return file_path

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
