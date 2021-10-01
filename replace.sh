# __version__=1.0.6.7
for f in .travis.yml activate_devel_env install_tools.sh LICENSE odoo_default_tnl.csv odoo_default_tnl.xlsx README.rst; do
  echo "\$ cp ./$f ~/tools/"
  cp ./$f ~/tools/
done
for item in egg-info docs tests templates license_text; do
  echo "\$ rsync -av ./$item/ ~/tools/$item/"
  rsync -av ./$item/ ~/tools/$item/
done
[[ -f ~/tools/install_foreign.sh ]] && rm -f ~/tools/install_foreign.sh
cd ~/tools
echo "\$ ./install_tools.sh -fgtq"
./install_tools.sh -fgtq
