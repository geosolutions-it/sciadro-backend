from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from dataclasses import dataclass
from typing import List
from typing import Union
from typing import BinaryIO


@dataclass
class Status:
    class_: str
    confidence: int


@dataclass
class Box:
    x_min: int
    y_min: int
    x_max: int
    y_max: int


@dataclass
class Object:
    id: int
    type: str
    status: Status
    type: str
    box: Box


@dataclass
class Position:
    longitude: float
    latitude: float


@dataclass
class Id:
    index: int
    database: str


@dataclass
class Size:
    width: int
    height: int
    depth: int


@dataclass
class Frame:
    id: Id
    position: Position
    size: Size
    objects: List[Object]


@dataclass
class Source:
    file_name: str
    path: str


@dataclass
class Root:
    type: str
    source: Source
    frames: List[Frame]


def _parse_id(node: Element) -> Id:
    return Id(
        index=int(node.find('index').text),
        database=node.find('database').text
    )


def _parse_position(node: Element) -> Position:
    return Position(
        longitude=float(node.find('longitude').text),
        latitude=float(node.find('latitude').text)
    )


def _parse_size(node: Element) -> Size:
    return Size(
        width=int(node.find('width').text),
        height=int(node.find('height').text),
        depth=int(node.find('depth').text)
    )


def _parse_status(node: Element) -> Status:
    return Status(
        class_=node.find('class').text,
        confidence=int(node.find('confidence').text)
    )


def _parse_box(node: Element) -> Box:
    return Box(
        x_min=int(node.find('xmin').text),
        y_min=int(node.find('ymin').text),
        x_max=int(node.find('xmax').text),
        y_max=int(node.find('ymax').text)
    )


def _parse_object(node: Element) -> Object:
    return Object(
        id=int(node.find('id').text),
        type=node.find('type').text,
        status=_parse_status(node.find('status')),
        box=_parse_box(node.find('box'))
    )


def _parse_frame(node: Element) -> Frame:
    return Frame(
        id=_parse_id(node.find('id')),
        position=_parse_position(node.find('pose')),
        size=_parse_size(node.find('size')),
        objects=list(map(_parse_object, node.find('objects').findall('object')))
    )


def _parse_source(node: Element) -> Source:
    return Source(
        file_name=node.find('filename').text,
        path=node.find('path').text
    )


def _parse_root(node: Element) -> Root:
    return Root(
        type=node.tag,
        source=_parse_source(node.find('source')),
        frames=list(map(_parse_frame, node.findall('frame')))
    )


def parse_asset_data(file_name: Union[str, BinaryIO]) -> Root:
    tree = ElementTree.parse(file_name)
    root = tree.getroot()
    return _parse_root(root)
