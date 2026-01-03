import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestE2ERenameScans(unittest.TestCase):
    """End-to-end tests for the rename_scans.py script."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dirpath = self.temp_dir.name
        self.script = os.path.abspath("rename_scans.py")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def create_test_file(self, filename: str) -> None:
        filepath = os.path.join(self.dirpath, filename)
        Path(filepath).touch()

    def run_script(self, mode: str, apply: bool = False) -> subprocess.CompletedProcess[str]:
        cmd = [
            "uv",
            "run",
            "python",
            self.script,
            "--mode",
            mode,
            self.dirpath,
        ]
        if apply:
            cmd.insert(3, "--apply")
        env = os.environ.copy()
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        print(result.stdout)
        print(result.stderr)
        return result

    def test_script_requires_mode(self) -> None:
        result = subprocess.run(
            ["python3", self.script, self.dirpath],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, result.returncode)

    def test_script_requires_target(self) -> None:
        result = subprocess.run(
            ["python3", self.script, "--mode", "two_sides"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, result.returncode)

    def test_script_dry_run_on_single_file(self) -> None:
        self.create_test_file("document.pdf")
        result = self.run_script("two_sides", apply=False)
        print(result.stdout)
        print(result.stderr)
        self.assertEqual(0, result.returncode)
        self.assertIn("Would rename", result.stdout)

    def test_script_without_apply_flag_does_not_rename(self) -> None:
        self.create_test_file("document.pdf")
        result = self.run_script("two_sides", apply=False)
        self.assertEqual(0, result.returncode)
        # Original file should still exist
        self.assertTrue(os.path.exists(os.path.join(self.dirpath, "document.pdf")))

    def test_script_on_file_target(self) -> None:
        self.create_test_file("document.pdf")
        file_path = os.path.join(self.dirpath, "document.pdf")

        cmd = [
            "python3",
            self.script,
            "--mode",
            "two_sides",
            file_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(0, result.returncode)

    def test_script_creates_git_commits(self) -> None:
        self.create_test_file("document.pdf")
        result = self.run_script("two_sides", apply=False)
        self.assertEqual(0, result.returncode)
        # Check that git was initialized
        git_dir = os.path.join(self.dirpath, ".git")
        self.assertTrue(os.path.isdir(git_dir))

    def test_script_with_multiple_files(self) -> None:
        self.create_test_file("Page_1.pdf")
        self.create_test_file("Page_2_1.pdf")
        self.create_test_file("Page_2_2.pdf")
        self.create_test_file("Page_3_1.pdf")

        result = self.run_script("two_sides", apply=False)
        self.assertEqual(0, result.returncode)

    def test_script_handles_special_characters(self) -> None:
        self.create_test_file("document_special-chars_1.pdf")
        result = self.run_script("two_sides", apply=False)
        self.assertEqual(0, result.returncode)
        self.assertIn("Would rename", result.stdout)

    def test_script_with_no_files_in_directory(self) -> None:
        os.makedirs(os.path.join(self.dirpath, "subdir"), exist_ok=True)
        result = self.run_script("two_sides", apply=False)
        self.assertEqual(0, result.returncode)
        self.assertIn("No files to rename", result.stdout)

    def test_script_handles_files_without_extensions(self) -> None:
        self.create_test_file("document")
        result = self.run_script("two_sides", apply=False)
        self.assertEqual(0, result.returncode)
        self.assertIn("Would rename", result.stdout)

    def test_script_filters_system_files(self) -> None:
        self.create_test_file("document.pdf")
        self.create_test_file(".DS_Store")
        self.create_test_file("Thumbs.db")

        result = self.run_script("two_sides", apply=False)
        self.assertEqual(0, result.returncode)
        # Only the PDF should be listed for renaming
        rename_count = result.stdout.count("Would rename")
        self.assertEqual(1, rename_count)

    def test_script_exit_code_on_success(self) -> None:
        self.create_test_file("document.pdf")
        result = self.run_script("two_sides", apply=False)
        self.assertEqual(0, result.returncode)

    def test_script_invalid_mode_fails(self) -> None:
        self.create_test_file("document.pdf")
        cmd = [
            "python3",
            self.script,
            "--mode",
            "invalid_mode",
            self.dirpath,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(0, result.returncode)


if __name__ == "__main__":
    unittest.main()
