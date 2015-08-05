'''
    Sample for pytok unit test
'''

import sys


class Parent_Class(object):
    def __init__(self):
        self.myvalue = 0

    def do_something(self):
        return self.myvalue


class My_Class():
    def __init__(self):
        pass

    def do_something(self):
        def _do_locally(val):
            val -= 1
            return val
        val = 1
        return _do_locally(val)

My_Class()


class My_Sub_Class(My_Class):
    _inherit = 'res.partner'

    def __init__(self):
        pass

    def search(self):
        m_obj = self.search()
        return m_obj

    def browse(self, ids):
        return self.browse(ids)

My_Sub_Class()


# Follow class is just to fill white paper!
class dummy:    # no useful class

    # Hidden function
    def do_nothing():   # nothing to do
        pass

    # Function without class call
    @staticmethod
    def do_public():
        return 0


class My_Child(Parent_Class):

    uresponse = 42

    @classmethod
    def universal_response(cls):
        return cls.uresponse

    def do_something(self):
        v = super(My_Child, self).do_something()
        if v == 0:
            return self.universal_response()

    def do_think_different(self, value):
        if value > 0:
            def _think_positive(value):
                return value
        elif value < 0:
            def _think_negative(value):
                return 0
            return _think_negative(value)
        else:
            def _think_positive(value):
                value += 1
                return value
        return _think_positive(value)


def main():
    # tool main
    sts = dummy.do_public()
    if sts == 0:
        A = My_Class()
        sts = A.do_something()
    if sts == 0:
        sts = Parent_Class().do_something()
    if sts == 0:
        sts = My_Child().do_something() - 42
    if sts == 0:
        M = My_Child()
        sts = 1 - M.do_think_different(1)
    if sts == 0:
        sts = 1 - M.do_think_different(0)
    if sts == 0:
        sts = M.do_think_different(-1)
    return sts


if __name__ == "__main__":
    sts = main()
    if sts:
        raise ValueError
    sys.exit(sts)
