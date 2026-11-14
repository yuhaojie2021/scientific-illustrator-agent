"""Editable scientific components; geometry is in artboard-relative points."""
from typing import List, Literal, Optional
from pydantic.v1 import Field, root_validator, validator
from models.figure_spec import SpecModel, TextStyle


class Vertex(SpecModel):
    id: str = Field(regex=r'^[A-Za-z][A-Za-z0-9_-]{0,63}$')
    x: float
    y: float
    label: str = ''
    features: List[str] = Field(default_factory=list)

    @validator('features', each_item=True)
    def colors(cls, value):
        return TextStyle.valid_color(value)


class Edge(SpecModel):
    source: str
    target: str
    color: str = '#657783'
    _color = validator('color', allow_reuse=True)(TextStyle.valid_color.__func__)


class Component(SpecModel):
    id: str = Field(regex=r'^[A-Za-z][A-Za-z0-9_-]{0,63}$')
    type: Literal['matrix', 'graph', 'feature_strip', 'text']
    x: float = 0
    y: float = 0
    title: str = ''
    font: str = 'ArialMT'
    font_size: float = Field(default=10, ge=6, le=100)
    cell_size: float = Field(default=14, gt=0, le=200)
    cells: List[List[str]] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    row_label: str = ''
    column_label: str = ''
    nodes: List[Vertex] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    node_radius: float = Field(default=4, gt=0, le=50)

    @root_validator
    def structure(cls, v):
        kind = v.get('type')
        cells = v.get('cells', [])
        if kind == 'matrix':
            if not cells or not cells[0] or any(len(r) != len(cells[0]) for r in cells):
                raise ValueError('Matrix must have nonempty rectangular cells')
        for row in cells:
            for color in row:
                TextStyle.valid_color(color)
        for color in v.get('features', []):
            TextStyle.valid_color(color)
        if kind == 'feature_strip' and not v.get('features'):
            raise ValueError('Feature strip requires colors')
        nodes = v.get('nodes', [])
        ids = [n.id for n in nodes]
        if kind == 'graph' and not nodes:
            raise ValueError('Graph requires nodes')
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate graph node IDs')
        for edge in v.get('edges', []):
            if edge.source not in ids or edge.target not in ids:
                raise ValueError('Dangling graph edge')
        return v


class Link(SpecModel):
    id: str = Field(regex=r'^[A-Za-z][A-Za-z0-9_-]{0,63}$')
    source: str
    target: str
    label: str = ''


class ComponentScene(SpecModel):
    scene_id: str = Field(regex=r'^[A-Za-z][A-Za-z0-9_-]{0,63}$')
    width: float = Field(default=700, gt=0, le=16383)
    height: float = Field(default=350, gt=0, le=16383)
    components: List[Component] = Field(min_items=1)
    links: List[Link] = Field(default_factory=list)

    @root_validator
    def references(cls, v):
        components, links = v.get('components', []), v.get('links', [])
        ids = [c.id for c in components]
        all_ids = ids + [l.id for l in links]
        if len(all_ids) != len(set(all_ids)):
            raise ValueError('Duplicate component or link ID')
        for link in links:
            if link.source not in ids or link.target not in ids or link.source == link.target:
                raise ValueError('Links require two distinct existing components')
        return v


def expected_counts(scene):
    counts = dict(cells=0, nodes=0, edges=0, feature_cells=0, texts=0, arrows=len(scene.links))
    for c in scene.components:
        counts['texts'] += bool(c.title)
        if c.type == 'matrix':
            counts['cells'] += sum(map(len, c.cells))
            counts['texts'] += bool(c.row_label) + bool(c.column_label)
        if c.type == 'feature_strip':
            counts['feature_cells'] += len(c.features)
        if c.type == 'graph':
            counts['nodes'] += len(c.nodes)
            counts['edges'] += len(c.edges)
            counts['feature_cells'] += sum(len(n.features) for n in c.nodes)
            counts['texts'] += sum(bool(n.label) for n in c.nodes)
    counts['texts'] += sum(bool(l.label) for l in scene.links)
    return counts
