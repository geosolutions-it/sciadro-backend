from dataclasses import dataclass
from typing import Type
from typing import Any
from uuid import UUID
from rest_framework.viewsets import ModelViewSet


PARENT_DESCRIPTOR = 'parent_descriptor'


@dataclass
class ParentDescriptor:
    class_: Type[Any]
    pk_name: str
    attr_name: str


class NestedViewSetMixin(ModelViewSet):
    def __init__(self, *args, **kwargs):
        self._descriptor = {}
        self._read_descriptor()
        self._parent_pk = None
        super().__init__(*args, **kwargs)

    def _read_descriptor(self):
        if hasattr(self, PARENT_DESCRIPTOR):
            descriptor = getattr(self.__class__, PARENT_DESCRIPTOR)
            self._descriptor['class'] = descriptor.class_
            self._descriptor['pk_name'] = descriptor.pk_name
            self._descriptor['attr_name'] = descriptor.attr_name
        else:
            raise ValueError('No parent descriptor')

    def create(self, request, *args, **kwargs):
        if self._descriptor['pk_name'] in kwargs:
            self._parent_pk = UUID(kwargs[self._descriptor['pk_name']])
        else:
            raise ValueError('No parent pk found')
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        parent = self._descriptor['class'].objects.get(pk=self._parent_pk)
        return serializer.save(**{self._descriptor['attr_name']: parent})
