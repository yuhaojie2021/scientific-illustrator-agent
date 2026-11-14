import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from models.component_spec import ComponentScene, expected_counts


class ComponentTests(unittest.TestCase):
    def sample(self):
        return json.loads((ROOT / 'examples/specs/components_demo.json').read_text())

    def test_counts(self):
        counts = expected_counts(ComponentScene.parse_obj(self.sample()))
        self.assertEqual(counts, dict(cells=12, nodes=3, edges=2, feature_cells=6, texts=5, arrows=1))

    def test_ragged_matrix(self):
        data = self.sample()
        data['components'][0]['cells'][0].pop()
        with self.assertRaises(ValueError):
            ComponentScene.parse_obj(data)

    def test_dangling_node(self):
        data = self.sample()
        data['components'][1]['edges'][0]['source'] = 'unknown'
        with self.assertRaises(ValueError):
            ComponentScene.parse_obj(data)

    def test_dangling_component(self):
        data = self.sample()
        data['links'][0]['target'] = 'unknown'
        with self.assertRaises(ValueError):
            ComponentScene.parse_obj(data)

    def test_duplicate_ids(self):
        data = self.sample()
        data['components'][1]['id'] = data['components'][0]['id']
        with self.assertRaises(ValueError):
            ComponentScene.parse_obj(data)

    def test_nonfinite_and_typo(self):
        for key,value in [('x',float('nan')),('colour','#000000')]:
            data = self.sample()
            data['components'][0][key] = value
            with self.assertRaises(ValueError):
                ComponentScene.parse_obj(data)

    def test_invalid_color(self):
        data = self.sample()
        data['components'][0]['cells'][0][0] = 'brown'
        with self.assertRaises(ValueError):
            ComponentScene.parse_obj(data)


if __name__ == '__main__':
    unittest.main()
