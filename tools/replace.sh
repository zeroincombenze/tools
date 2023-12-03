# __version__=2.0.5
if [[ -z $HOME_DEVEL ]]; then
    [[ -d $HOME/odoo/devel ]] && HOME_DEVEL="$HOME/odoo/devel" || HOME_DEVEL="$HOME/devel"
fi
tgtdir=$(readlink -f $HOME_DEVEL/..)/tools
for f in install_tools.sh LICENSE odoo_template_tnl.xlsx README.rst; do
    echo "\$ cp ./$f $tgtdir/"
    cp ./$f $tgtdir/
done
for item in egg-info docs tests templates license_text; do
    echo "\$ rsync -a ./$item/ $tgtdir/$item/"
    rsync -a ./$item/ $tgtdir/$item/
done
echo "\$ cp ../.readthedocs.yml $tgtdir/"
cp ../.readthedocs.yml $tgtdir/
[[ -f $tgtdir/install_foreign.sh ]] && rm -f $tgtdir/install_foreign.sh
# cd $tgtdir
# ./install_tools.sh -T

