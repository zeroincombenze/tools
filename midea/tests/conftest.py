# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures for midea tests.
"""
import pytest


@pytest.fixture
def something_instance():
    """Return a fresh MideaDoSomething instance with a known action."""
    from midea.scripts.midea_do_something import MideaDoSomething
    return MideaDoSomething("show")
