import unittest
import os
import subprocess
import tempfile
import json

class TestJson2IfcPipeline(unittest.TestCase):
    def setUp(self):
        self.script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'json2ifc.py'))
        self.output_dir = tempfile.mkdtemp()

    def tearDown(self):
        for f in os.listdir(self.output_dir):
            os.remove(os.path.join(self.output_dir, f))
        os.rmdir(self.output_dir)

    def run_script(self, input_json, output_ifc):
        result = subprocess.run([
            'python', self.script,
            '--input_json', input_json,
            '--output_ifc', output_ifc
        ], capture_output=True, text=True)
        return result

    def test_valid_wall(self):
        input_data = {
            "walls": [
                {
                    "id": "wall1",
                    "storey": 1,
                    "start_point": [0, 0],
                    "end_point": [1, 0],
                    "thickness": 0.2,
                    "material": "Concrete",
                    "z_placement": 0.0,
                    "height": 2.5,
                    "openings": []
                }
            ]
        }
        input_json = os.path.join(self.output_dir, 'valid_wall.json')
        output_ifc = os.path.join(self.output_dir, 'valid_wall.ifc')
        with open(input_json, 'w') as f:
            json.dump(input_data, f)
        result = self.run_script(input_json, output_ifc)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(output_ifc))

    def test_missing_input_json(self):
        output_ifc = os.path.join(self.output_dir, 'missing.ifc')
        result = self.run_script('missing_file.json', output_ifc)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Input JSON not found', result.stderr)

    def test_invalid_wall_geometry(self):
        input_data = {
            "walls": [
                {
                    "id": "wall1",
                    "storey": 1,
                    "thickness": 0.2,
                    "material": "Concrete",
                    "z_placement": 0.0,
                    "height": 2.5,
                    "openings": []
                }
            ]
        }
        input_json = os.path.join(self.output_dir, 'invalid_wall.json')
        output_ifc = os.path.join(self.output_dir, 'invalid_wall.ifc')
        with open(input_json, 'w') as f:
            json.dump(input_data, f)
        result = self.run_script(input_json, output_ifc)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('missing', result.stderr)

    def test_multiple_storeys_and_walls(self):
        input_data = {
            "storeys": [
                {"name": "Ground", "elevation": 0.0},
                {"name": "First", "elevation": 3.0}
            ],
            "walls": [
                {
                    "id": "wall1",
                    "storey": 1,
                    "start_point": [0, 0],
                    "end_point": [1, 0],
                    "thickness": 0.2,
                    "material": "Concrete",
                    "z_placement": 0.0,
                    "height": 2.5,
                    "openings": []
                },
                {
                    "id": "wall2",
                    "storey": 2,
                    "start_point": [0, 1],
                    "end_point": [1, 1],
                    "thickness": 0.2,
                    "material": "Concrete",
                    "z_placement": 3.0,
                    "height": 2.5,
                    "openings": []
                }
            ]
        }
        input_json = os.path.join(self.output_dir, 'multi_storey.json')
        output_ifc = os.path.join(self.output_dir, 'multi_storey.ifc')
        with open(input_json, 'w') as f:
            json.dump(input_data, f)
        result = self.run_script(input_json, output_ifc)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(output_ifc))

if __name__ == '__main__':
    unittest.main()
