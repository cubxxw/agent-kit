from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / 'skills/excalidraw-architecture/scripts/render-excalidraw.mjs'


class DiagramDeliveryTests(unittest.TestCase):
    def scene(self) -> dict:
        return {
            'type': 'excalidraw', 'version': 2,
            'appState': {'viewBackgroundColor': '#ffffff'},
            'elements': [{'id': 'source', 'type': 'rectangle', 'x': 0, 'y': 0,
                          'width': 160, 'height': 80, 'strokeColor': '#111111',
                          'backgroundColor': '#ffffff', 'strokeStyle': 'solid'}],
            'files': {},
        }

    def test_export_preserves_input_even_without_excalidraw_extension(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'scene.json'
            source.write_text(json.dumps(self.scene()))
            before = source.read_bytes()
            subprocess.run(['node', str(RENDER), str(source)], check=True, capture_output=True)
            self.assertEqual(before, source.read_bytes())
            self.assertIn('<svg', Path(str(source) + '.svg').read_text())
            alias = Path(directory) / 'alias.svg'
            alias.symlink_to(source)
            result = subprocess.run(['node', str(RENDER), str(source), '--svg', str(alias)], capture_output=True)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(before, source.read_bytes())

    def test_unsafe_attributes_and_unsupported_elements_preserve_previous_export(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'scene.excalidraw'
            output = Path(directory) / 'scene.svg'
            for field, value in [('backgroundColor', '#fff\" onload=\"alert(1)'), ('type', 'image')]:
                with self.subTest(field=field):
                    scene = self.scene()
                    scene['elements'][0][field] = value
                    source.write_text(json.dumps(scene))
                    output.write_text('trusted previous export')
                    result = subprocess.run(['node', str(RENDER), str(source)], capture_output=True)
                    self.assertNotEqual(0, result.returncode)
                    self.assertEqual('trusted previous export', output.read_text())

    def test_all_five_archify_modes_deliver_frozen_bytes_and_reproduce_goldens(self):
        skill = ROOT / 'skills/archify'
        examples = [
            ('architecture', 'web-app.architecture.json', 'web-app-rendered.html'),
            ('workflow', 'agent-tool-call.workflow.json', 'workflow-agent-tool-call-rendered.html'),
            ('sequence', 'cache-miss-request.sequence.json', 'sequence-cache-miss-request.html'),
            ('dataflow', 'product-analytics.dataflow.json', 'dataflow-product-analytics.html'),
            ('lifecycle', 'agent-run.lifecycle.json', 'lifecycle-agent-run.html'),
        ]
        with tempfile.TemporaryDirectory() as directory:
            for mode, example, golden in examples:
                with self.subTest(mode=mode):
                    source = skill / 'examples' / example
                    target = Path(directory) / (mode + '.html')
                    result = subprocess.run([
                        'node', str(skill / 'bin/archify.mjs'), 'deliver', mode,
                        str(source), str(target), '--quality', 'showcase', '--json',
                    ], check=True, text=True, capture_output=True)
                    receipt = json.loads(result.stdout)
                    self.assertTrue(receipt['ok'])
                    self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), receipt['specification']['sha256'])
                    self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), receipt['artifact']['sha256'])
                    subprocess.run([
                        'node', str(skill / f'renderers/{mode}/render-{mode}.mjs'),
                        str(source), str(target),
                    ], check=True, capture_output=True)
                    self.assertEqual((skill / 'examples' / golden).read_bytes(), target.read_bytes())
