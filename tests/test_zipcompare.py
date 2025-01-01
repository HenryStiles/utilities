import unittest
import zipfile
import os
from scripts.zipcompare import (
    compare_zip_and_directory,
    ZipFileNotFoundError,
    DirectoryNotFoundError
)

class TestZipCompare(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up temporary test files and directories."""
        cls.test_zip = 'test_zip.zip'
        cls.test_dir = 'test_dir'
        cls.mismatch_zip = 'mismatch_zip.zip'
        cls.empty_zip = 'empty_zip.zip'
        os.makedirs(cls.test_dir, exist_ok=True)
        
        # Create matching ZIP and directory
        with zipfile.ZipFile(cls.test_zip, 'w') as zipf:
            zipf.writestr('file1.txt', 'Hello, World!')
            zipf.writestr('folder/file2.txt', 'Another file')
        
        os.makedirs(os.path.join(cls.test_dir, 'folder'), exist_ok=True)
        with open(os.path.join(cls.test_dir, 'file1.txt'), 'w') as f:
            f.write('Hello, World!')
        with open(os.path.join(cls.test_dir, 'folder/file2.txt'), 'w') as f:
            f.write('Another file')
        
        # Create mismatched ZIP
        with zipfile.ZipFile(cls.mismatch_zip, 'w') as zipf:
            zipf.writestr('file1.txt', 'Different content')
            zipf.writestr('folder/file2.txt', 'Another file')
        
        # Create an empty ZIP
        with zipfile.ZipFile(cls.empty_zip, 'w') as zipf:
            pass

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary files and directories."""
        os.remove(cls.test_zip)
        os.remove(cls.mismatch_zip)
        os.remove(cls.empty_zip)
        for root, dirs, files in os.walk(cls.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(cls.test_dir)

    def test_valid_comparison(self):
        """Test matching ZIP and directory."""
        result = compare_zip_and_directory(self.test_zip, self.test_dir)
        self.assertEqual(result['only_in_zip'], set())
        self.assertEqual(result['only_in_dir'], set())
        self.assertEqual(result['size_mismatch'], {})

    def test_size_mismatch(self):
        """Test size mismatch detection."""
        result = compare_zip_and_directory(self.mismatch_zip, self.test_dir)
        self.assertIn('file1.txt', result['size_mismatch'])
        self.assertEqual(result['only_in_zip'], set())
        self.assertEqual(result['only_in_dir'], set())

    def test_empty_zip(self):
        """Test comparison with an empty ZIP file."""
        result = compare_zip_and_directory(self.empty_zip, self.test_dir)
        self.assertEqual(result['only_in_zip'], set())
        self.assertEqual(set(result['only_in_dir']), {'file1.txt', 'folder/file2.txt'})
        self.assertEqual(result['size_mismatch'], {})

    def test_missing_zip_file(self):
        with self.assertRaises(ZipFileNotFoundError):
            compare_zip_and_directory('non_existent.zip', self.test_dir)

    def test_missing_directory(self):
        with self.assertRaises(DirectoryNotFoundError):
            compare_zip_and_directory(self.test_zip, 'non_existent_dir')


if __name__ == '__main__':
    unittest.main()
