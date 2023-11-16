
::

    deploy_odoo update -r {{repos_name}} -b {{branch}} -G {{GIT_ORGID}} -p $HOME/{{branch}}
    vem amend $HOME/{{branch}}/venv_odoo
    # Adjust following statements as per your system
    sudo systemctl restart odoo
