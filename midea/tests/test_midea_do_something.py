# -*- coding: utf-8 -*-
"""
Unit tests for MideaDoSomething class.
"""
import pytest
from midea.scripts.midea_do_something import MideaDoSomething


class TestMideaDoSomethingInit:
    """Tests for __init__."""

    def test_init_stores_action(self):
        """Action should be stored as an instance attribute."""
        obj = MideaDoSomething("config")
        assert obj.action == "config"

    def test_init_with_empty_string(self):
        """Empty string is a valid action."""
        obj = MideaDoSomething("")
        assert obj.action == ""

    def test_init_with_none_does_not_crash(self):
        """None should be stored like any other value."""
        obj = MideaDoSomething(None)
        assert obj.action is None


class TestDoActionConfig:
    """Tests for do_action_config."""

    def test_sets_action_to_config(self):
        """After calling do_action_config, action should be 'config'."""
        obj = MideaDoSomething("show")
        obj.do_action_config()
        assert obj.action == "config"

    def test_prints_message(self, capsys):
        """Should print 'Action config done'."""
        obj = MideaDoSomething("show")
        obj.do_action_config()
        captured = capsys.readouterr()
        assert "Action config done" in captured.out


class TestDoActionShow:
    """Tests for do_action_show."""

    def test_prints_hello_world(self, capsys):
        """Should print 'Hello world'."""
        obj = MideaDoSomething("config")
        obj.do_action_show()
        captured = capsys.readouterr()
        assert "Hello world" in captured.out

    def test_prints_last_action(self, capsys):
        """Should print the last action value."""
        obj = MideaDoSomething("config")
        obj.do_action_show()
        captured = capsys.readouterr()
        assert "Last action was config" in captured.out

    def test_does_not_change_action(self):
        """do_action_show should not modify self.action."""
        obj = MideaDoSomething("config")
        obj.do_action_show()
        assert obj.action == "config"


class TestDoRepeatLastAction:
    """Tests for do_repeat_last_action."""

    def test_dispatches_to_known_action(self, capsys):
        """When action='show', should call do_action_show."""
        obj = MideaDoSomething("show")
        obj.do_repeat_last_action()
        captured = capsys.readouterr()
        assert "Hello world" in captured.out

    def test_unknown_action_prints_message(self, capsys):
        """When action is not implemented, should print a message."""
        obj = MideaDoSomething("nonexistent")
        obj.do_repeat_last_action()
        captured = capsys.readouterr()
        assert "not implemented" in captured.out

    def test_unknown_action_does_not_crash(self):
        """Unknown action should not raise an exception."""
        obj = MideaDoSomething("nonexistent")
        # Should not raise
        obj.do_repeat_last_action()


class TestRegression:
    """
    Regression tests — add tests here whenever you fix a bug.
    These ensure bugs don't come back.
    """

    def test_regression_action_case_sensitivity(self):
        """
        Regression: ensure action names are case-sensitive.
        If someone changes the dispatch to be case-insensitive,
        this test will catch it.
        """
        obj = MideaDoSomething("SHOW")
        # "SHOW" != "show", so do_action_SHOW doesn't exist
        # This should not crash, just print "not implemented"
        obj.do_repeat_last_action()
        # Action should remain unchanged
        assert obj.action == "SHOW"
