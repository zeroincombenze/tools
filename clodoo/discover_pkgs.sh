# 0.1.2
if [ "$(basename $PWD)" == "addons" ]; then
  root_dir=..
else
  root_dir=.
fi
echo "searching for 'import ...'"
find . -name "*.py" -exec grep -Eo "^ *import [A-Za-z0-9_,]+" '{}' \;|awk '{print $2 $3 $4 $5 $6 $7 $8 $9}'|tr "," "\n"|tr " " "\n">~/discover_pkgs.log
echo "searching for 'from . import ...'"
find . -name "*.py" -exec grep -Eo "^ *from [A-Za-z0-9_]+ import [A-Za-z0-9_,]+" '{}' \;|awk '{print $2}'|tr "," "\n"|tr " " "\n">>~/discover_pkgs.log
echo "searching for exclusions ..."
O=$(find . -name "*.py" -exec grep -Eo " _name *= *['\"][A-Za-z0-9_-]+['\"]" '{}' \;|awk -F= '{print $2}'|tr -d "'"|tr -d '"'|sort -bf|uniq|tr -d "\r"|tr "\n" " ")
# echo "$O"
D=$(find $root_dir -type d -not -path '*/.git/*' -not -name '.git'|xargs -I'{}' basename {}|sort -bf|uniq|tr -d "\r"|tr "\n" " ")
F=$(find $root_dir -type f -name '*.py' -not -name "_*"|xargs -I'{}' basename {}|sort -bf|uniq|awk -F. '{print $1}'|tr -d "\r"|tr "\n" " ")
X=$(pip list --format columns|awk '{print tolower($1)}'|tr -d "\r"|tr "\n" " ")
P="array ast base64 BaseHTTPServer behave calendar cgi cPickle collections contextlib copy cStringIO datetime decimal errno difflib email encodings ftplib functools glob hashlib heapq html2text imaplib inspect itertools locale logging mailbox odoo opcode openerp openobject OpenSSL operator optparse orm os osv poplib pprint Queue random setproctitle sets setuptools shutil SimpleHTTPServer socket ssl string StringIO struct subprocess support sys System tarfile tempfile textwrap threading tidy time traceback types urllib urllib2 urlparse UserDict weakref xmlrpclib zipfile"
if [ "$1" == "-n" ]; then
  if [ -n "$2" ]; then
    cat ~/discover_pkgs.log|sort -bf|uniq -i|tr "\n" " "|grep --color $2
    echo "O=<$O>"|grep --color $2
    echo "D=<$D>"|grep --color $2
    echo "P=<$P>"|grep --color $2
    echo "F=<$F>"|grep --color $2
    # echo "<$X>"|grep --color $2
  else
    cat ~/discover_pkgs.log|sort -bf|uniq -i|tr "\n" " "
    echo "O=<$O>"
    echo "D=<$D>"
    echo "P=<$P>"
    echo "F=<$F>"
    # echo "<$X>"
  fi
  exit 1
fi
echo "analyzing names ..."
sed -e "s/etree/lxml/" -i ~/discover_pkgs.log
sed -e "s/^openid/python-openid/" -i ~/discover_pkgs.log
sed -e "s/^psycopg2$/psycopg2-binary/" -i ~/discover_pkgs.log
sed -e "s/^werkzeug$/Werkzeug/" -i ~/discover_pkgs.log
sed -e "s/^jinja2$/Jinja2/" -i ~/discover_pkgs.log
sed -e "s/^dateutil$/python-dateutil/" -i ~/discover_pkgs.log
sed -e "s/^docutils$/python-docutils/" -i ~/discover_pkgs.log
sed -e "s/^simplejson$/python-simplejson/" -i ~/discover_pkgs.log
echo "----------------------------------"
for f in $(cat ~/discover_pkgs.log|sort -bf|uniq -i|tr "\n" " "); do
  if [[ ! "${f:0:1}" == "_" && ! "${f^^}" == "$f" && ! "${f:0:5}" == "test_" && ! "${f:0:5}" == "win32" ]]; then
    if [[ ! \ $O\  =~ \ $f\  ]]; then
      # if [[ ! \ $X\  =~ \ $f\  ]]; then
        if [[ ! \ $D\  =~ \ $f\  ]]; then
          if [[ ! \ $F\  =~ \ $f\  ]]; then
            if [[ ! \ $P\  =~ \ $f\  ]]; then
              echo "$f"
            fi
          fi
        fi
      # fi
    fi
  fi
done

