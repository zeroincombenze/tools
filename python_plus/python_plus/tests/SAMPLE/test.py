
from z0lib import z0lib
parser = z0lib.parseoptargs("Test","(C) SHS-AV",version="1.2.3.4")
parser.add_argument('-h')
parser.add_argument('-V')
ctx = parser.parseoptargs(['-V'])
