#! /bin/bash
# Zip data and export to cloudpepper (Ridix)
[[ -z $1 || $1 == -h || $1 == --help ]] && echo -e "$(basename $0)\n[-N][--no-cloudpepper][--source=SOURCE] date # $(date +%d-%m-%Y)" && exit 1
[[ $1 == -V ]] && echo "2.0.0" && exit 1

param=""
sts=0
while [[ -n "$1" ]]; do
    [[ -z $1 ]] &&  sts=1
    [[ $sts -eq 0 && -n $param ]] && eval $param="$1" && param="" && sts=1
    [[ $sts -eq 0 && $1 =~ --dry-run ]] && DRY_RUN=1 && sts=1
    [[ $sts -eq 0 && $1 =~ --no-cloudpepper ]] && NO_CLOUDPEPPER=1 && sts=1
    [[ $sts -eq 0 && $1 =~ --source= ]] && x=$(echo $1|cut -d= -f2) && SOURCE="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --source ]] && param="SOURCE" && sts=1
    [[ $sts -eq 0 && $1 =~ --target= ]] && x=$(echo $1|cut -d= -f2) && TARGET="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --target ]] && param="TARGET" && sts=1
    [[ $sts -eq 0 && $1 =~ -.*n ]] && DRY_RUN=1 && sts=1
    [[ $sts -eq 0 && $1 =~ -.*N ]] && NO_CLOUDPEPPER=1 && sts=1
    [[ $sts -eq 0 && $1 =~ -.*v ]] && VERBOSE="-v" && sts=1
    [[ $sts -eq 0 && $1 =~ [0-9\-]{10} ]] && DATE="$1" && sts=1
    [[ $sts -eq 0 ]] && echo "Unknow value $1"
    shift
    sts=0
done

# Custom values
PREFIX="OneDrive_1_"
[[ -z $DATE ]] && DATE=$(date +%d-%m-%Y)
[[ -z $DRY_RUN ]] && DRY_RUN=0
[[ -z $NO_CLOUD_PEPPER ]] && NO_CLOUDPEPPER=1 && sts=1
[[ -z $SOURCE_PATH ]] && SOURCE_PATH="/home/antoniov/Scaricati"
[[ -z $SOURCE ]] && SOURCE="$SOURCE_PATH/$PREFIX$DATE" && SOURCE_PATH=$(dirname $SOURCE)
[[ -z $TARGET ]] && TARGET="/home/odoo/ridix"

if [[ ! -d "$SOURCE" && -f "$SOURCE.zip" ]]; then
  SRC_FN=$(basename $SOURCE)
  echo cd "$SOURCE_PATH"
	cd "$SOURCE_PATH"
  echo unzip $SRC_FN.zip -d $SRC_FN
	[[ $DRY_RUN -eq 0 ]] && unzip $SRC_FN.zip -d $SRC_FN
fi
[[ ! -d "$SOURCE" ]]	&& echo "Data $SOURCE not found!" && ls -l $SOURCE_PATH/$PREFIX* && exit 1

[[ ! -d $TARGET ]]	&& echo "Directory $TARGET not found!" && exit 1
echo cd $TARGET
cd $TARGET
echo "sudo rm *.csv"
[[ $DRY_RUN -ne 0 ]] && sudo rm *.csv
echo "sudo cp $SOURCE/*.csv ./"
[[ $DRY_RUN -eq 0 ]] && sudo cp $SOURCE/*.csv ./
# echo cd /mnt/c/Users/anton/OneDrive/Documenti/Clienti/Ridix/Import\ Dati/Correzioni/
# cd /mnt/c/Users/anton/OneDrive/Documenti/Clienti/Ridix/Import\ Dati/Correzioni/
echo -e "\n"
echo "===[Contents of local /home/odoo&ridix]==="
ls /home/odoo/ridix
echo -e "\n"
if [[ $NO_CLOUDPEPPER -eq 0 ]]; then
  echo ssh.py cloudpepper -c "rm /var/odoo/ridix/*.csv"
  [[ $DRY_RUN -eq 0 ]] && ssh.py cloudpepper -c "rm /var/odoo/ridix/*.csv"
  for fn in *.csv; do
    echo $fn
    [[ $DRY_RUN -eq 0 ]] && ssh.py -s $fn cloudpepper:/var/odoo/ridix
  done
fi
