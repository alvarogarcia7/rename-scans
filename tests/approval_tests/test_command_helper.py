import unittest

from tests.approval_tests.command_helper import CommandHelper


class MyTestCase(unittest.TestCase):
    def test_split_by_multiple_spaces(self) -> None:
        self.assertEqual(['a', 'b'], self.to_list('a b'))
        self.assertEqual(['a', 'b'], self.to_list('a  b'))

    def test_remove_end_of_line(self) -> None:
        self.assertEqual(['a', 'b'], self.to_list("""\
    a b
    """))
        self.assertEqual(['a', 'b'], self.to_list('a  b'))

    def to_list(self, param: str) -> list[str]:
        return CommandHelper().to_list(param)


if __name__ == '__main__':
    unittest.main()
