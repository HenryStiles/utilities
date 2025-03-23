import unittest
from unittest.mock import patch, mock_open
from io import StringIO
import sys
from scripts.classextract import extract_class_text_from_files

class TestClassExtract(unittest.TestCase):
    def setUp(self):
        # Capture stdout for testing output
        self.held, sys.stdout = sys.stdout, StringIO()

    def tearDown(self):
        # Reset stdout after testing
        sys.stdout = self.held

    def test_extract_class_text_success(self):
        """Test successful extraction of text from a class."""
        test_content = """
        <html>
        <body>
            <p class="myclass">This is test paragraph 1.</p>
            <p class="otherclass">This should not be included.</p>
            <p class="myclass">This is test paragraph 2.</p>
        </body>
        </html>
        """
        expected_output = """
File: mock_file.html
  Paragraph 1: This is test paragraph 1.
  Paragraph 2: This is test paragraph 2.
"""

        # Use patch to mock open, returning test_content
        with patch("builtins.open", mock_open(read_data=test_content)) as mock_file:
            extract_class_text_from_files("myclass", ["mock_file.html"])

        # Assert that open() was called correctly
        mock_file.assert_called_once_with("mock_file.html", "r", encoding="utf-8")

        # Check captured stdout matches expected
        self.assertEqual(sys.stdout.getvalue().strip(), expected_output.strip())

    def test_extract_class_text_no_match(self):
        """Test when no paragraphs match the specified class."""
        test_content = """
        <html>
        <body>
            <p class="otherclass">This should not be included.</p>
        </body>
        </html>
        """
        expected_output = """
File: mock_file.html
  No matching paragraphs found.
"""
        with patch("builtins.open", mock_open(read_data=test_content)) as mock_file:
            extract_class_text_from_files("myclass", ["mock_file.html"])

        mock_file.assert_called_once_with("mock_file.html", "r", encoding="utf-8")
        self.assertEqual(sys.stdout.getvalue().strip(), expected_output.strip())

    def test_extract_multiple_files(self):
        """Test when multiple files are provided."""
        test_content1 = """
        <html>
        <body>
            <p class="myclass">File 1, Paragraph 1</p>
        </body>
        </html>
        """
        test_content2 = """
        <html>
        <body>
            <p class="myclass">File 2, Paragraph 1</p>
            <p class="myclass">File 2, Paragraph 2</p>
        </body>
        </html>
        """
        expected_output = """
File: mock_file1.html
  Paragraph 1: File 1, Paragraph 1
File: mock_file2.html
  Paragraph 1: File 2, Paragraph 1
  Paragraph 2: File 2, Paragraph 2
"""
        with patch("builtins.open") as mock_file:
            mock_file.side_effect = [
                mock_open(read_data=test_content1).return_value,
                mock_open(read_data=test_content2).return_value
            ]
            extract_class_text_from_files("myclass", ["mock_file1.html", "mock_file2.html"])
        
        actual_output = sys.stdout.getvalue()
        # Remove extra newlines for comparison
        actual_output_lines = [line.strip() for line in actual_output.splitlines() if line.strip()]
        expected_output_lines = [line.strip() for line in expected_output.splitlines() if line.strip()]

        self.assertEqual(actual_output_lines, expected_output_lines)
        mock_file.assert_any_call("mock_file1.html", "r", encoding="utf-8")
        mock_file.assert_any_call("mock_file2.html", "r", encoding="utf-8")
    
    def test_file_not_found(self):
        """Test when a file is not found."""
        expected_output = "Error: File not found - non_existent.html\n"
        with patch("builtins.open", side_effect=FileNotFoundError) as mock_file:
            extract_class_text_from_files("myclass", ["non_existent.html"])
        self.assertEqual(sys.stdout.getvalue().strip(), expected_output.strip())

if __name__ == '__main__':
    unittest.main()
