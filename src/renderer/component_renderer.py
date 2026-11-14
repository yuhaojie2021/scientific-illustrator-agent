"""Build and verify a replacement scene before removing its previous version."""
import json
from pathlib import Path
from illustrator.com_client import IllustratorClient
from models.component_spec import expected_counts


def render_components(scene, target='new', expected_document=None):
    if target == 'active' and not expected_document:
        raise ValueError('Active-document rendering requires --expected-document from inspect')
    source = (Path(__file__).parents[1] / 'illustrator/jsx/serialize.jsx').read_text(encoding='utf-8') + '\n' + Path(__file__).with_name('components.jsx').read_text(encoding='utf-8')
    payload = dict(scene=scene.dict(), target=target, expected_document=expected_document,
                   expected=expected_counts(scene))
    script = '(function(P){\n' + source + '\n})(' + json.dumps(payload, ensure_ascii=True, allow_nan=False) + ');'
    with IllustratorClient() as client:
        return json.loads(client.execute_jsx(script, owned_document=False))
