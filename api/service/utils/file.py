from .nested import NestedViewSetMixin


FILE_HANDLER = 'file_handler'


class FileHandlerMixin(NestedViewSetMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._file_handler = None
        self._read_file_handler()

    def _read_file_handler(self):
        if hasattr(self, FILE_HANDLER):
            self._file_handler = getattr(self.__class__, FILE_HANDLER)
        else:
            raise ValueError('No file handler')

    def perform_create(self, serializer):
        instance = super().perform_create(serializer)
        self._file_handler.delay(instance.id)
        return instance
