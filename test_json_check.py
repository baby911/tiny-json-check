import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from json_check import MAX_BYTES, validate

SCRIPT = str(Path(__file__).with_name("json_check.py"))


class ValidationTests(unittest.TestCase):
    def test_valid_values_and_unicode(self):
        for value in [None, True, 42, 1.5, "你好", [], {"a": [{"b": 1}]}]:
            validate(json.dumps(value, ensure_ascii=False).encode("utf-8"))

    def test_duplicate_keys_at_any_depth(self):
        for data in [b'{"a":1,"a":2}', b'{"x":{"a":1,"a":2}}',
                     b'{"a":1,"\\u0061":2}']:
            with self.assertRaisesRegex(ValueError, "duplicate"):
                validate(data)

    def test_same_key_in_separate_objects_is_valid(self):
        validate(b'[{"a":1},{"a":2}]')

    def test_nonstandard_constants(self):
        for data in [b'NaN', b'Infinity', b'-Infinity', b'{"a":NaN}']:
            with self.assertRaisesRegex(ValueError, "non-standard"):
                validate(data)

    def test_syntax_errors(self):
        for data in [b'', b'{"a":}', b'{} {}', b'[1,]', b'01']:
            with self.assertRaises(ValueError):
                validate(data)

    def test_utf8(self):
        validate(b'\xef\xbb\xbf{}')
        with self.assertRaises(ValueError):
            validate(b'"\xff"')

    def test_large_numbers(self):
        validate(b'[1e9999,' + b'1' * 5000 + b']')

    def test_size_limit(self):
        with self.assertRaisesRegex(ValueError, "10 MiB"):
            validate(b' ' * (MAX_BYTES + 1))

    def test_stdin_and_exit_status(self):
        for data, code in [(b'{}', 0), (b'{', 1)]:
            result = subprocess.run([sys.executable, SCRIPT, '-'], input=data,
                                    capture_output=True)
            self.assertEqual(result.returncode, code)

    def test_multiple_files_continue_after_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            good = Path(folder) / 'good.json'
            good.write_bytes(b'{"hello":"world"}')
            original = good.read_bytes()
            result = subprocess.run([sys.executable, SCRIPT,
                                     str(Path(folder) / 'missing.json'), str(good)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('OK ' + str(good), result.stdout)
            self.assertEqual(good.read_bytes(), original)

    def test_repeated_stdin_is_usage_error(self):
        result = subprocess.run([sys.executable, SCRIPT, '-', '-'],
                                input=b'{}', capture_output=True)
        self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
