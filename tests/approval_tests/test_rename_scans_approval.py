import os
import tempfile
import unittest
from pathlib import Path

import approvaltests
from app.mode_two_sides import two_sides
from app.domain import MoveResult


class TestRenameScanApprovals(unittest.TestCase):
    """Approval tests for rename_scans functionality using relative paths."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dirpath = Path(self.temp_dir.name)
        self.original_cwd = os.getcwd()
        os.chdir(self.dirpath)

    def tearDown(self) -> None:
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()

    def create_test_file(self, filename: str) -> None:
        Path(filename).touch()

    def test_approval_single_file_rename(self) -> None:
        """Approval test for renaming a single file."""
        self.create_test_file("document.pdf")

        files = [str(self.dirpath / "document.pdf")]
        result = two_sides(files, self.dirpath, apply_changes=False)

        output = self._format_result_with_relative_paths(result)
        approvaltests.verify(output)

    def test_approval_multiple_files_with_trailing_numbers(self) -> None:
        """Approval test for renaming files with trailing numbers."""
        self.create_test_file("scana.pdf")
        self.create_test_file("scanb_1.pdf")
        self.create_test_file("scanc_8_1.pdf")

        files = [str(self.dirpath / f) for f in ["scana.pdf", "scanb_1.pdf", "scanc_8_1.pdf"]]
        result = two_sides(files, self.dirpath, apply_changes=False)

        output = self._format_result_with_relative_paths(result)
        approvaltests.verify(output)

    def test_approval_padding_two_digits(self) -> None:
        """Approval test for file padding with 10+ files."""
        for i in range(10):
            self.create_test_file(f"doc_{i}.pdf")

        files = [str(self.dirpath / f"doc_{i}.pdf") for i in range(10)]
        result = two_sides(files, self.dirpath, apply_changes=False)

        output = self._format_result_with_relative_paths(result)
        approvaltests.verify(output)

    def test_approval_files_without_extension(self) -> None:
        """Approval test for renaming files without extension."""
        self.create_test_file("documenta")
        self.create_test_file("documentb_1")

        files = [str(self.dirpath / f) for f in ["documenta", "documentb_1"]]
        result = two_sides(files, self.dirpath, apply_changes=False)

        output = self._format_result_with_relative_paths(result)
        approvaltests.verify(output)

    def test_approval_mixed_file_types(self) -> None:
        """Approval test for renaming mixed file types."""
        self.create_test_file("pagea.pdf")
        self.create_test_file("pageb_1.jpg")
        self.create_test_file("pagec_2.png")
        self.create_test_file("paged_8_1.gif")

        files = [str(self.dirpath / f) for f in ["pagea.pdf", "pageb_1.jpg", "pagec_2.png", "paged_8_1.gif"]]
        result = two_sides(files, self.dirpath, apply_changes=False)

        output = self._format_result_with_relative_paths(result)
        approvaltests.verify(output)

    def test_approval_no_files(self) -> None:
        """Approval test for empty directory."""
        result = two_sides([], self.dirpath, apply_changes=False)

        output = self._format_result_with_relative_paths(result)
        approvaltests.verify(output)

    def test_approval_three_digit_padding(self) -> None:
        """Approval test for file padding with 100+ files."""
        for i in range(100, 103):
            self.create_test_file(f"doc_{i}.pdf")

        files = [str(self.dirpath / f"doc_{i}.pdf") for i in range(100, 103)]
        result = two_sides(files, self.dirpath, apply_changes=False)

        output = self._format_result_with_relative_paths(result)
        approvaltests.verify(output)

    def test_approval_special_characters_in_filename(self) -> None:
        """Approval test for special characters in filenames."""
        self.create_test_file("document_special-chars_1.pdf")
        self.create_test_file("file_with_spaces_2.pdf")

        files = [str(self.dirpath / f) for f in ["document_special-chars_1.pdf", "file_with_spaces_2.pdf"]]
        result = two_sides(files, self.dirpath, apply_changes=False)

        output = self._format_result_with_relative_paths(result)
        approvaltests.verify(output)

    def _format_result_with_relative_paths(self, result: MoveResult) -> str:
        """Format result using relative paths instead of absolute paths."""
        output_lines = []

        output_lines.append(f"Return Code: {result.returncode}")
        output_lines.append(f"Processed Files: {result.processed_files}")
        output_lines.append(f"Success: {result.success}")
        output_lines.append("")

        output_lines.append("Messages:")
        for msg in result.messages:
            relative_msg = self._make_relative(msg)
            output_lines.append(f"  {relative_msg}")

        if result.renames:
            output_lines.append("")
            output_lines.append("Renames:")
            for rename in result.renames:
                old_rel = self._make_relative(rename.old_path)
                new_rel = self._make_relative(rename.new_path)
                output_lines.append(f"  {old_rel} -> {new_rel}")

        return "\n".join(output_lines)

    def _make_relative(self, text: str) -> str:
        """Convert absolute paths in text to relative paths."""
        dirpath_str = str(self.dirpath)

        if dirpath_str in text:
            text = text.replace(dirpath_str + "/", "")

        return text


if __name__ == "__main__":
    unittest.main()
