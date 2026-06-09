#!/usr/bin/env python
# -*- coding: utf-8 -*-


class MideaDoSomething:

    def __init__(self, action):
        self.action = action

    def do_action_config(self):
        print("Action config done")
        self.action = "config"

    def do_action_show(self):
        print("Hello world")
        print("Last action was %s" % self.action)

    def do_repeat_last_action(self):
        if hasattr(self, "do_action_%s" % self.action):
            getattr(self, "do_action_%s" % self.action)()
        else:
            print("Action %s not implemented" % self.action)
