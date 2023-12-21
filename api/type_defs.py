from typing import TypedDict, Literal, Optional, NotRequired


class Shape(TypedDict):
    start_x: int
    start_y: int
    end_x: int
    end_y: int


class ShapeExternal(TypedDict):
    x: list[int]
    y: list[int]


class Relation(TypedDict):
    type: Literal["child", "parent"]
    label_id: str


class Meta(TypedDict):
    confirmed: bool
    confidence_percent: float


class AnnotationDict(TypedDict):
    id: str
    class_id: Literal["tooth", "caries"]
    shape: Shape
    relations: NotRequired[list[Relation]]
    tags: NotRequired[list[str]]
    surface: NotRequired[list[str]]
    meta: Meta


class AnnotationFlatDict(TypedDict):
    id: str
    class_id: Literal["tooth", "caries"]
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    confirmed: bool
    confidence_percent: float
    tags: NotRequired[list[str]]
    surface: NotRequired[list[str]]
    parent: NotRequired[str]


class AnnotationExternalDict(TypedDict):
    kind: Literal["tooth", "caries"]
    shape: ShapeExternal
    number: NotRequired[str]
    surface: NotRequired[str]
    children: NotRequired[list['AnnotationExternalDict']]
