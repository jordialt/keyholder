import unittest
from unittest.mock import patch, MagicMock, call
import os
import sys
import tempfile

import main


class TestKeyholder(unittest.TestCase):

    def setUp(self):
        # Use a temp file for the index so tests don't touch the real one
        self.tmp_index = tempfile.NamedTemporaryFile(delete=False, suffix="_index")
        self.tmp_index.close()
        self._index_patcher = patch.object(main, "INDEX_PATH", self.tmp_index.name)
        self._index_patcher.start()

        # Suppress migration prompt during tests
        self._migrate_patcher = patch.object(main, "LEGACY_CONFIG_PATH", "/tmp/_no_such_file_.json")
        self._migrate_patcher.start()

    def tearDown(self):
        self._index_patcher.stop()
        self._migrate_patcher.stop()
        if os.path.exists(self.tmp_index.name):
            os.remove(self.tmp_index.name)

    # ── set ────────────────────────────────────────────────────────────

    @patch("keyring.set_password")
    def test_set_key(self, mock_set):
        main.set_key("openai", "sk-abc123")
        mock_set.assert_called_once_with("keyholder", "openai", "sk-abc123")
        self.assertIn("openai", main._load_index())

    # ── get ────────────────────────────────────────────────────────────

    @patch("pyperclip.copy")
    @patch("keyring.get_password", return_value="sk-abc123")
    @patch("keyring.set_password")
    def test_get_key(self, mock_set, mock_get, mock_copy):
        main.set_key("openai", "sk-abc123")
        main.get_key("openai", timeout=0)
        mock_copy.assert_called_with("sk-abc123")

    @patch("keyring.get_password", return_value=None)
    def test_get_key_not_found(self, mock_get):
        with self.assertRaises(SystemExit) as cm:
            main.get_key("nonexistent", timeout=0)
        self.assertEqual(cm.exception.code, 1)

    # ── list ───────────────────────────────────────────────────────────

    @patch("keyring.set_password")
    def test_list_keys(self, mock_set):
        main.set_key("a_service", "k1")
        main.set_key("b_service", "k2")
        names = main._load_index()
        self.assertEqual(names, {"a_service", "b_service"})

    # ── remove ─────────────────────────────────────────────────────────

    @patch("keyring.delete_password")
    @patch("keyring.set_password")
    def test_remove_key(self, mock_set, mock_del):
        main.set_key("s1", "k1")
        main.set_key("s2", "k2")
        main.remove_key("s1")
        mock_del.assert_called_once_with("keyholder", "s1")
        self.assertNotIn("s1", main._load_index())
        self.assertIn("s2", main._load_index())

    @patch("keyring.delete_password")
    def test_remove_key_not_found(self, mock_del):
        with self.assertRaises(SystemExit) as cm:
            main.remove_key("ghost")
        self.assertEqual(cm.exception.code, 1)
        mock_del.assert_not_called()

    # ── clipboard auto-clear ──────────────────────────────────────────

    @patch("pyperclip.copy")
    def test_clipboard_clear_timer(self, mock_copy):
        """Timer should fire and call pyperclip.copy('') after timeout."""
        import time
        main._schedule_clipboard_clear(1)
        time.sleep(1.5)
        mock_copy.assert_called_with("")

    # ── migration ─────────────────────────────────────────────────────

    @patch("keyring.set_password")
    @patch("builtins.input", return_value="y")
    def test_migration(self, mock_input, mock_set):
        import json
        legacy = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
        json.dump({"openai": "sk-1", "anthropic": "sk-2"}, legacy)
        legacy.close()

        with patch.object(main, "LEGACY_CONFIG_PATH", legacy.name):
            main._maybe_migrate()

        self.assertEqual(mock_set.call_count, 2)
        self.assertFalse(os.path.exists(legacy.name))
        index = main._load_index()
        self.assertIn("openai", index)
        self.assertIn("anthropic", index)


if __name__ == "__main__":
    unittest.main()
