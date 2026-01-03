import os
import tempfile
import unittest
from pathlib import Path

from app.domain import MoveAction, MoveResult
from app.mode_two_sides import two_sides, strip_trailing_number_groups


class TestStripTrailingNumberGroups(unittest.TestCase):
    """Test the strip_trailing_number_groups function."""

    def test_no_trailing_numbers(self) -> None:
        result = strip_trailing_number_groups("document")
        self.assertEqual("document", result)

    def test_single_trailing_number_with_space(self) -> None:
        result = strip_trailing_number_groups("document 1")
        self.assertEqual("document", result)

    def test_single_trailing_number_with_underscore(self) -> None:
        result = strip_trailing_number_groups("document_1")
        self.assertEqual("document", result)

    def test_single_trailing_number_with_hyphen(self) -> None:
        result = strip_trailing_number_groups("document-1")
        self.assertEqual("document", result)

    def test_two_trailing_numbers_with_spaces(self) -> None:
        result = strip_trailing_number_groups("document 8 1", times=2)
        self.assertEqual("document", result)

    def test_two_trailing_numbers_mixed_separators(self) -> None:
        result = strip_trailing_number_groups("document_8-1", times=2)
        self.assertEqual("document", result)

    def test_strip_only_one_when_times_is_one(self) -> None:
        result = strip_trailing_number_groups("document_8_1", times=1)
        self.assertEqual("document_8", result)


class TestTwoSides(unittest.TestCase):
    """Test the two_sides function."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dirpath = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def create_test_file(self, filename: str) -> str:
        filepath = os.path.join(str(self.dirpath), filename)
        Path(filepath).touch()
        return filepath

    def test_no_files_returns_zero_result(self) -> None:
        result = two_sides([], self.dirpath, apply_changes=False)
        self.assertEqual(0, result.returncode)
        self.assertEqual(0, result.processed_files)

    def test_single_file_with_no_suffix(self) -> None:
        file1 = self.create_test_file("document.pdf")
        result = two_sides([file1], self.dirpath, apply_changes=False)
        self.assertEqual(0, result.returncode)
        self.assertEqual(1, result.processed_files)

    def test_padding_single_digit(self) -> None:
        files = [self.create_test_file(f"doc_{i}.pdf") for i in range(9)]
        result = two_sides(files, self.dirpath, apply_changes=False)
        self.assertEqual(0, result.returncode)

    def test_padding_two_digits(self) -> None:
        files = [self.create_test_file(f"doc_{i}.pdf") for i in range(10)]
        result = two_sides(files, self.dirpath, apply_changes=False)
        self.assertEqual(0, result.returncode)

    def test_padding_three_digits(self) -> None:
        files = [self.create_test_file(f"doc_{i}.pdf") for i in range(100)]
        result = two_sides(files, self.dirpath, apply_changes=False)
        self.assertEqual(0, result.returncode)

    def test_apply_changes_dry_run(self) -> None:
        file1 = self.create_test_file("document.pdf")
        result = two_sides([file1], self.dirpath, apply_changes=False)
        self.assertEqual(0, result.returncode)
        # File should still exist with original name
        self.assertTrue(os.path.exists(file1))

    def test_apply_changes_actual_rename(self) -> None:
        file1 = self.create_test_file("documenta.pdf")
        result = two_sides([file1], self.dirpath, apply_changes=True)
        self.assertEqual(0, result.returncode)
        self.assertEqual(1, result.processed_files)
        # Original file should not exist
        self.assertFalse(os.path.exists(file1))

    def test_file_without_extension(self) -> None:
        file1 = self.create_test_file("document")
        result = two_sides([file1], self.dirpath, apply_changes=False)
        self.assertEqual(0, result.returncode)
        self.assertEqual(1, result.processed_files)

    def test_messages_contain_success_indicator(self) -> None:
        file1 = self.create_test_file("document.pdf")
        result = two_sides([file1], self.dirpath, apply_changes=False)
        self.assertEqual(0, result.returncode)
        self.assertTrue(any("Success" in msg for msg in result.messages))


if __name__ == "__main__":
    unittest.main()
