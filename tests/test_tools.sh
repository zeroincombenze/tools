echo "source ~/devel/activate_tools"
source ~/devel/activate_tools
for pkg in clodoo.py cvt_csv_2_rst.py cvt_csv_2_xml.py gen_addons_table.py gen_readme.py inv2draft_n_restore.py list_requirements makepo_it.py odoo_dependencies.py odoo_shell.py odoo_translation.py to_pep8.py transodoo.py wget_odoo_repositories.py; do
    echo "Testing $pkg --version .."
    $pkg -V
done
