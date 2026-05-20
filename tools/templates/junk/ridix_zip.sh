[[ -z $1 ]] && echo "$0 date [-n] # dd-mm-yyyy -n -> No cloudpepper" && exit 1
cd $(dirname $0)
if [[ ! -d "/mnt/c/Users/anton/OneDrive/Documenti/Clienti/Ridix/Import Dati/OneDrive_1_$1" ]]; then
    if [[ ! -d "/mnt/c/Users/anton/OneDrive/Documenti/Clienti/Ridix/Import Dati/OneDrive_1_${1}.zip" ]]; then
        echo cd "/mnt/c/Users/anton/OneDrive/Documenti/Clienti/Ridix/Import Dati/"
	cd "/mnt/c/Users/anton/OneDrive/Documenti/Clienti/Ridix/Import Dati/"
        echo unzip OneDrive_1_${1}.zip -d OneDrive_1_${1}
	unzip OneDrive_1_${1}.zip -d OneDrive_1_${1}
    fi
    [[ ! -d OneDrive_1_${1} ]]	&& echo "Data not found!" && exit 1
fi
echo rm ~/ridix/*.csv
rm ~/ridix/*.csv
echo cd /mnt/c/Users/anton/OneDrive/Documenti/Clienti/Ridix/Import\ Dati/OneDrive_1_$1/
cd /mnt/c/Users/anton/OneDrive/Documenti/Clienti/Ridix/Import\ Dati/OneDrive_1_$1/
echo cp *.csv /home/odoo/ridix
cp *.csv /home/odoo/ridix
echo cd /mnt/c/Users/anton/OneDrive/Documenti/Clienti/Ridix/Import\ Dati/Correzioni/
cd /mnt/c/Users/anton/OneDrive/Documenti/Clienti/Ridix/Import\ Dati/Correzioni/
echo cp *.csv /home/odoo/ridix
cp *.csv /home/odoo/ridix
echo -e "\n"
echo cd /home/odoo/ridix
cd /home/odoo/ridix
echo rm *:Zone.Identifier
for f in *Zone.Identifier; do rm $f; done
echo -e "\n"
ls /home/odoo/ridix
echo -e "\n"
if [[ -z $2 ]]; then
  echo ssh.py cloudpepper -c "rm /var/odoo/ridix/*.csv"
  ssh.py cloudpepper -c "rm /var/odoo/ridix/*.csv"
  for fn in *.csv; do
    echo $fn
    ssh.py -s $fn cloudpepper:/var/odoo/ridix
  done
fi

