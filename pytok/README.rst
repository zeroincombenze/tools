pytok
=====

Python simple tokenizer to select pieces of python code.

To use:
    >>> from pytok import pytok
    >>> SRC = []
    >>> SRC[0] = 'class myclass():'
    >>> SRC[1] = '   def myfun(self):'
    >>> SRC[2] = '       pass'
    >>> src = pytok.new(text=SRC)
    >>> src.decl_options(no_num_line=True)
    >>> src.decl_classes_2_search('myclass')
    >>> src.decl_funs_2_search('myfun')
    >>> src.decl_tokens_2_search('pass')
    >>> src.parse_src()
    >>> res = src.tostring()
    >>> print res
    class myclass():
        def myfun(self):
            pass


For furthermore info see: http://wiki.zeroincombenze.org/it/Python/opt/pytok

