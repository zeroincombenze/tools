# lisa setup 0.2.36.25 (2017-11-02 20:05)
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
pkgname=lisa
tarball=lisa.tar.gz
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
if [ -f $TDIR/z0librc -o $opt_dry_run -gt 0 ]; then
  [ $opt_dry_run -gt 0 ] || . $TDIR/z0librc
  if [ "$TDIR" != "/usr/bin" ]; then
    if [ "${TDIR:0:14}" == "/opt/odoo/dev/" ]; then
      cpmv="cp"
    else
      cpmv="mv"
    fi
    [ $opt_verbose -gt 0 ] && echo "$pfx mkdir -p /etc/lisa"
    [ $opt_dry_run -gt 0 ] || mkdir -p /etc/lisa
    for f in lisa lisa.man lisa_bld_ods; do
      if [ -f $TDIR/$f ]; then
        [ $opt_verbose -gt 0 ] && echo "$pfx $cpmv $TDIR/$f /usr/bin"
        [ $opt_dry_run -gt 0 ] || eval $cpmv $TDIR/$f /usr/bin
      fi
    done
    [ $opt_verbose -gt 0 ] && echo "$pfx chmod +x /usr/bin/$pkgname*"
    [ $opt_dry_run -gt 0 ] || chmod +x /usr/bin/$pkgname*
    for f in lisa.conf.sample odoo-server_Debian odoo-server_RHEL odoo-server LAMP.lish lisa.lish odoo.lish postgresql.lish python.lish; do
      if [ -f $TDIR/$f ]; then
        [ $opt_verbose -gt 0 ] && echo "$pfx $cpmv $TDIR/$f /etc/lisa"
        [ $opt_dry_run -gt 0 ] || eval $cpmv $TDIR/$f /etc/lisa
      fi
    done
    [ $opt_verbose -gt 0 ] && echo "$pfx cd $TDIR"
    [ $opt_dry_run -gt 0 ] || cd $TDIR
    [ $opt_verbose -gt 0 ] && echo "$pfx _install_z0librc"
    [ $opt_dry_run -gt 0 ] || _install_z0librc
    [ $opt_verbose -gt 0 ] && echo "$pfx cd .."
    [ $opt_dry_run -gt 0 ] || cd ..
    if [ -d "./$pkgname" ]; then
      [ $opt_verbose -gt 0 ] && echo "rm -fR ./$pkgname"
      [ $opt_dry_run -gt 0 ] || rm -fR ./$pkgname
    fi
    if [ -f "./$tarball" ]; then
      [ $opt_verbose -gt 0 ] && echo "rm -f ./$tarball"
      [ $opt_dry_run -gt 0 ] || rm -f ./$tarball
    fi
  fi
else
  echo "Library z0librc not found!"
  exit 1
fi
