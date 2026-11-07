import unittest

from code_engine import analyze_code, clean_code, compare_code, safety_scan


class TestCodeEngine(unittest.TestCase):
    def test_clean_code(self):
        self.assertEqual(clean_code("```python\nprint('hi')\n```"), "print('hi')")

    def test_python_analysis(self):
        metrics = analyze_code("def add(a, b):\n    return a + b\n", "Python")
        self.assertEqual(metrics["functions"], 1)
        self.assertIsNone(metrics["syntax_error"])

    def test_safety(self):
        result = safety_scan("import os\nos.system('whoami')", "Python")
        self.assertFalse(result["safe"])

    def test_diff(self):
        result = compare_code("a=1\n", "a = 1\n")
        self.assertGreaterEqual(result["added"], 1)
        self.assertGreaterEqual(result["removed"], 1)


if __name__ == "__main__":
    unittest.main()
