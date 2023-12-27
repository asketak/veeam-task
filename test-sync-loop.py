import unittest
import os
import shutil
from sync_loop import sync_folders  # Import the sync_folders function from your script

class TestFolderSync(unittest.TestCase):

    def setUp(self):
        self.source_dir = "test_source"
        self.replica_dir = "test_replica"
        os.makedirs(self.source_dir, exist_ok=True)
        os.makedirs(self.replica_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.source_dir)
        shutil.rmtree(self.replica_dir)

    def create_file(self, directory, filename, content="default content"):
        with open(os.path.join(directory, filename), "w") as f:
            f.write(content)

    def test_add_file_to_source(self):
        self.create_file(self.source_dir, "new_file.txt")
        sync_folders(self.source_dir, self.replica_dir)
        self.assertTrue(os.path.exists(os.path.join(self.replica_dir, "new_file.txt")))

    def test_delete_file_from_source(self):
        self.create_file(self.source_dir, "delete_me.txt")
        sync_folders(self.source_dir, self.replica_dir)
        os.remove(os.path.join(self.source_dir, "delete_me.txt"))
        sync_folders(self.source_dir, self.replica_dir)
        self.assertFalse(os.path.exists(os.path.join(self.replica_dir, "delete_me.txt")))

    def test_modify_file_in_source(self):
        self.create_file(self.source_dir, "modify_me.txt")
        sync_folders(self.source_dir, self.replica_dir)
        self.create_file(self.source_dir, "modify_me.txt", "new content")
        sync_folders(self.source_dir, self.replica_dir)
        with open(os.path.join(self.replica_dir, "modify_me.txt"), "r") as f:
            content = f.read()
        self.assertEqual(content, "new content")

    def test_add_directory_to_source(self):
        os.makedirs(os.path.join(self.source_dir, "new_dir"))
        sync_folders(self.source_dir, self.replica_dir)
        self.assertTrue(os.path.exists(os.path.join(self.replica_dir, "new_dir")))

    def test_delete_directory_from_source(self):
        os.makedirs(os.path.join(self.source_dir, "delete_dir"))
        sync_folders(self.source_dir, self.replica_dir)
        shutil.rmtree(os.path.join(self.source_dir, "delete_dir"))
        sync_folders(self.source_dir, self.replica_dir)
        self.assertFalse(os.path.exists(os.path.join(self.replica_dir, "delete_dir")))

    def test_overwrite_changes_in_replica(self):
        self.create_file(self.source_dir, "file.txt", "source content")
        sync_folders(self.source_dir, self.replica_dir)
        self.create_file(self.replica_dir, "file.txt", "replica content")
        sync_folders(self.source_dir, self.replica_dir)
        with open(os.path.join(self.replica_dir, "file.txt"), "r") as f:
            content = f.read()
        self.assertEqual(content, "source content")

    def test_remove_directory_with_files_in_source(self):
        os.makedirs(os.path.join(self.source_dir, "dir_to_remove"))
        self.create_file(os.path.join(self.source_dir, "dir_to_remove"), "file_in_dir.txt")
        sync_folders(self.source_dir, self.replica_dir)
        shutil.rmtree(os.path.join(self.source_dir, "dir_to_remove"))
        sync_folders(self.source_dir, self.replica_dir)
        self.assertFalse(os.path.exists(os.path.join(self.replica_dir, "dir_to_remove")))
        self.assertFalse(os.path.exists(os.path.join(self.replica_dir, "dir_to_remove", "file_in_dir.txt")))

if __name__ == '__main__':
    unittest.main()
