"""Evaluate workflow annotations without requiring Django application setup."""
import ast
import typing
import unittest
from pathlib import Path


class Python38AnnotationTests(unittest.TestCase):
    def test_workflow_annotations_evaluate_on_supported_python(self):
        root = Path(__file__).resolve().parents[1] / 'backend_boilerplate'
        for filename in ('utils/models.py', 'notifications/template_renderer.py', 'scrutiny/workflow.py'):
            tree = ast.parse((root / filename).read_text())
            namespace = vars(typing).copy()
            namespace['Context'] = type('Context', (), {})
            for node in ast.walk(tree):
                annotation = None
                if isinstance(node, ast.arg):
                    annotation = node.annotation
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    annotation = node.returns
                if annotation is not None:
                    with self.subTest(filename=filename, line=node.lineno):
                        eval(compile(ast.Expression(annotation), filename, 'eval'), namespace)


if __name__ == '__main__':
    unittest.main()
