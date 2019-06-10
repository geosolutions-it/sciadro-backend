from io import BytesIO
from unittest import TestCase

from service.file_streaming_wrapper import RangeFileWrapper


class TestFileWrapper(TestCase):

    def test_read_file_by_chunk(self):
        file = BytesIO()
        test_value = b'Test value Test value Test value Test value Test value Test value'
        input_len = len(test_value)
        file.write(test_value)
        file.seek(0)
        wrapper = RangeFileWrapper(file, chunk=25, offset=0, length=input_len)
        read_len = 0
        for chunk in wrapper:
            read_len += len(chunk)
        wrapper.close()

        self.assertEqual(input_len, read_len)



    def test_read_file_at_once(self):
        file = BytesIO()
        test_value = b'Test value Test value Test value Test value Test value Test value'
        input_len = len(test_value)
        file.write(test_value)
        file.seek(0)
        wrapper = RangeFileWrapper(file, chunk=25, offset=0)
        read_len = 0
        for chunk in wrapper:
            read_len += len(chunk)
        wrapper.close()

        self.assertEqual(input_len, read_len)
