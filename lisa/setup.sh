# lisa setup 0.3.1.2 (2018-08-21 09:19)
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
pkgname=lisa
if [ -d $TDIR/$pkgname ]; then
  SRCDIR=$TDIR/$pkgname
else
  SRCDIR=$TDIR
fi
tarball=$pkgname.tar.gz
opt_verbose=0
opt_dry_run=0
if [ "${1:0:1}" == "-" ]; then
  if [[ "$1" =~ v ]]; then opt_verbose=1; fi
  if [[ "$1" =~ n ]]; then opt_dry_run=1; fi
fi
if [ ${opt_dry_run:-0} -eq 0 ]; then
  pfx="\$"
else
  pfx=">"
fi
if [ -f $SRCDIR/z0librc -o $opt_dry_run -gt 0 ]; then
  [ $opt_dry_run -gt 0 ] || . $SRCDIR/z0librc
  if [ "${TDIR:0:10}" == "/opt/odoo/" ]; then
    cpmv="cp"
  else
    cpmv="mv"
  fi
  [ $opt_verbose -gt 0 ] && echo "$pfx mkdir -p /etc/lisa"
  [ $opt_dry_run -gt 0 ] || mkdir -p /etc/lisa
  [ $opt_verbose -gt 0 ] && echo "$pfx mkdir -p /etc/lisa/kbase"
  [ $opt_dry_run -gt 0 ] || mkdir -p /etc/lisa/kbase
  for f in lisa lisa.man lisa_bld_ods lisa_set_ods stdout2wiki; do
    if [ -f $SRCDIR/$f ]; then
      [ $opt_verbose -gt 0 ] && echo "$pfx $cpmv $SRCDIR/$f /usr/bin"
      [ $opt_dry_run -gt 0 ] || eval $cpmv $SRCDIR/$f /usr/bin
      [ $opt_verbose -gt 0 ] && echo "$pfx [ -x /usr/bin/$f ] && chmod +x /usr/bin/$f"
      [[ $opt_dry_run > 0 && -x /usr/bin/$f ]] && chmod +x /usr/bin/$f
    fi
  done
  for f in lisa.conf.sample odoo-server_Debian odoo-server_RHEL odoo-server kbase/LAMP.lish kbase/LAMP_security.lish kbase/lisa.lish kbase/odoo.lish kbase/postgresql.lish kbase/python.lish; do
    if [ -f $SRCDIR/$f ]; then
      [ $opt_verbose -gt 0 ] && echo "$pfx $cpmv $SRCDIR/$f /etc/lisa"
      [ $opt_dry_run -gt 0 ] || eval $cpmv $SRCDIR/$f /etc/lisa/$f
    fi
  done
  if [ 1 -gt 0 ]; then
    [ $opt_verbose -gt 0 ] && echo "$pfx cd $SRCDIR"
    [ $opt_dry_run -gt 0 ] || cd $SRCDIR
    [ $opt_verbose -gt 0 ] && echo "$pfx _install_z0librc"
    [ $opt_dry_run -eq 0 ] && _install_z0librc
  fi
  if [ 1 -gt 0 ]; then
    [ $opt_verbose -gt 0 ] && echo "$pfx $cpmv $SRCDIR/odoorc /etc"
    [ $opt_dry_run -eq 0 ] && eval $cpmv $SRCDIR/odoorc /etc
  fi
  [ $opt_verbose -gt 0 ] && echo "$pfx cd $TDIR"
  [ $opt_dry_run -gt 0 ] || cd $TDIR
  if [ -d $TDIR/$pkgname ]; then
    [ $opt_verbose -gt 0 ] && echo "rm -fR $TDIR/$pkgname"
    [ $opt_dry_run -gt 0 ] || rm -fR $TDIR/$pkgname
  fi
  if [ -f "./$tarball" ]; then
    [ $opt_verbose -gt 0 ] && echo "rm -f ./$tarball"
    [ $opt_dry_run -gt 0 ] || rm -f ./$tarball
  fi
else
  echo "Library z0librc not found!"
  exit 1
fi
