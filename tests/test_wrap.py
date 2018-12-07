import unittest
from os import path
import json
import inspect

from .context import bted
import bted.definitions as definitions
from bted import interpreter

wrap_tests = path.join(definitions.TESTS_DIR, 'test_wrap.json')


class TestWrap(unittest.TestCase):

    def setUp(self):
        self.interpreter = interpreter.default_interpreter()
        with open(wrap_tests, 'r') as fin:
            self.tests = json.load(fin)

    def perform_test(self, command: [str], input_file: str, expected_result_file: str):
        with open(expected_result_file, 'r') as fin:
            expected = fin.read()
        cmd, flags = self.interpreter.build_command(command, input_file)
        res = self.interpreter.execute_command(cmd, flags, return_output=True)
        self.assertEqual(expected, res)

    def perform_test_from_key(self, key: str):
        tests = self.tests[key]
        for t in tests:
            self.perform_test(t["command"], path.join(definitions.TEST_FILES_DIR, t["input"]), path.join(definitions.TEST_FILES_DIR, t["expected"]))

    def test_wrap_word(self):
        func_name = inspect.stack()[0].function
        self.perform_test_from_key(func_name)

    def test_wrap_lines_containing_word(self):
        func_name = inspect.stack()[0].function
        self.perform_test_from_key(func_name)

    def test_wrap_lines_starting_with_word(self):
        func_name = inspect.stack()[0].function
        self.perform_test_from_key(func_name)

    def test_wrap_lines_ending_with_word(self):
        func_name = inspect.stack()[0].function
        self.perform_test_from_key(func_name)

    def test_wrap_lines_m_to_n_with_word(self):
        func_name = inspect.stack()[0].function
        self.perform_test_from_key(func_name)