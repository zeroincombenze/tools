# __version__=2.0.4
if [[ -z $HOME_DEVEL ]]; then
    [[ -d $HOME/odoo/devel ]] && HOME_DEVEL="$HOME/odoo/devel" || HOME_DEVEL="$HOME/devel"
fi
tgtdir=$(readlink -f $HOME_DEVEL/..)/tools
for f in .travis.yml install_tools.sh LICENSE odoo_default_tnl.xlsx odoo_template_tnl.xlsx README.rst; do
    echo "\$ cp ./$f $tgtdir/"
    cp ./$f $tgtdir/
done
for item in egg-info docs tests templates license_text; do
    echo "\$ rsync -a ./$item/ $tgtdir/$item/"
    rsync -a ./$item/ $tgtdir/$item/
done
[[ -f $tgtdir/install_foreign.sh ]] && rm -f $tgtdir/install_foreign.sh
# cd $tgtdir
# ./install_tools.sh -T
