import os


class RangeFileWrapper(object):

    def __init__(self, video_file, chunk=8192, offset=0, length=None):
        self.video_file = video_file
        self.video_file.seek(offset, os.SEEK_SET)
        self.to_read = length
        self.chunk = chunk

    def close(self):
        if hasattr(self.video_file, 'close'):
            self.video_file.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.to_read is None:
            # size is negative read whole file
            data = self.video_file.read(-1)
            if data:
                return data
            raise StopIteration()
        else:
            if self.to_read <= 0:
                raise StopIteration()
            data = self.video_file.read(min(self.to_read, self.chunk))
            if not data:
                raise StopIteration()
            self.to_read -= len(data)
            return data
