from __future__ import print_function, unicode_literals

__version__='0.1.0'


def utf8s(src):
    if isinstance(src, dict):
        for x in src.keys():
            src[x] = x.encode('utf-8')
    elif isinstance(src, list):
        for i,x in enumerate(src):
            src[i] = x.encode('utf-8')
    return src


def unicodes(src):
    if isinstance(src, dict):
        for x in src.keys():
            src[x] = unicode(x)
    elif isinstance(src, list):
        for i,x in enumerate(src):
            src[i] = unicode(x)
    return src


def qsplit(*args, **kwargs):
    src = args[0]
    if len(args) > 1 and args[1]:
        sep = args[1]
    else:
        sep=[' ', '\t', '\n', '\r']
    if len(args) > 2 and args[2]:
        maxsplit = args[2]
    else:
        maxsplit = -1
    q = kwargs.get('q', ["'", '"'])
    escape = kwargs.get('e', False)
    quoted = kwargs.get('quoted', False)
    strip = kwargs.get('strip', False)
    source = unicode(src)
    sts = False
    result = []
    item = ''
    esc_sts = False
    ctr = 0
    for ch in source:
        if maxsplit >= 0 and ctr >= maxsplit:
            item += ch
        elif esc_sts:
            esc_sts = False
            item += ch
        elif ch == escape:
            esc_sts = True
        elif ch == sts:
            sts = False
            if quoted:
                item += ch
        elif sts:
            item += ch
        elif ch in q:
            sts = ch
            if quoted:
                item += ch
        elif ((isinstance(sep, (tuple, list)) and ch in sep) or
              (isinstance(sep, basestring) and ch == sep)):
            if strip:
                result.append(item.strip())
            else:
                result.append(item)
            item = ''
            ctr += 1
        else:
            item += ch
    if strip:
        result.append(item.strip())
    else:
        result.append(item)
    if isinstance(src, str):
        return utf8s(result)
    return result
