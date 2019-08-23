__version__=0.2.1

THIS=$(basename $0)
FSQL=${THIS:0: -3}.sql
if [ "$HOSTNAME" == "erp" ]; then
  DEFDB=cscs2016
  # Solo scritture con user_id
  SELECT="h.create_uid in (36,95) or h.write_uid in (36,95)"
  # Aziende da dettagliare
  COMPANIES="1 3"
  # minimo importo fatturabile
  MIN="1"
  # mastri clienti/fornitori
  ACC_CF="'150100','250100'"
  # Sezionali da escludere
  JRNL_NAME_EXCL='%utofatture%'
else
  # Solo scritture con user_id
  SELECT=true
  # Aziende da dettagliare
  COMPANIES=
  # minimo importo fatturabile
  MIN="0.02"
  # mastri clienti/fornitori
  ACC_CF="'150100','250100'"
  # Sezionali da escludere
  JRNL_NAME_EXCL='%utofatture%'
fi

if [ -z "$1" ]; then
  if [ -z "$DEFDB" ]; then
    echo "$THIS db"
    exit 1
  else
   DB=$DEFDB
  fi
else
  DB=$1
fi
COMPANIES=$(psql $DB -tc "select id from res_company;")
X=$(psql $DB -tc "select id from account_account where code in ($ACC_CF);")
ACC_CLFO=$(echo $X)
ACC_CLFO="${ACC_CLFO// /,}"
echo "clfo>$ACC_CLFO:=select id from account_account where code in ($ACC_CF);"
X=$(psql $DB -tc "select id from account_journal where name like '$JRNL_NAME_EXCL';")
JRNL_EXCL=$(echo $X)
JRNL_EXCL="${JRNL_EXCL// /,}"
echo "clfo>$JRNL_EXCL:=select id from account_journal where name like '$JRNL_NAME_EXCL';"


show_tot(){
    if [ -z "$1" ]; then
      CPNY=""
      echo "======================================================="
    else
      CPNY="h.company_id=$1 and"
      echo "==========[Company id $1]================="
    fi
    SQLCMD="select count(id) from account_invoice h where $CPNY ($SELECT);"
    inv=$(psql $DB -tc "$SQLCMD"|grep -Eo "[0-9]+" |head -n1)
    echo "inv>$inv:=$SQLCMD"
    SQLCMD="select count(id) from account_move h where $CPNY ($SELECT);"
    gl=$(psql $DB -tc "$SQLCMD"|grep -Eo "[0-9]+" |head -n1)
    echo " gl>$gl:=$SQLCMD"
    if [ $gl -gt $inv ]; then
      let pay="$gl-$inv"
      rmd=0
    else
      pay=0
      let rmd="$inv-$gl"
    fi
    echo "pay>$pay:=$gl-$inv"
    if [ -n "$JRNL_EXCL" ]; then
      SQLCMD="select count(id) from account_invoice h where $CPNY (amount_total < $MIN or journal_id in ($JRNL_EXCL)) and ($SELECT);"
      inv0=$(psql $DB -tc "$SQLCMD"|grep -Eo "[0-9]+" |head -n1)
      echo "inv0>$inv0:=$SQLCMD"
    else
      SQLCMD="select count(id) from account_invoice h where $CPNY amount_total < $MIN and ($SELECT);"
      inv0=$(psql $DB -tc "$SQLCMD"|grep -Eo "[0-9]+" |head -n1)
      echo "inv0>$inv0:=$SQLCMD"
    fi
    SQLCMD="select count(*) from (select h.id from account_move h,account_move_line l where $CPNY l.move_id=h.id and ((l.credit>0 and l.credit<$MIN and l.id in ($ACC_CLFO)) or (l.debit>0 and l.debit<$MIN and l.id in ($ACC_CLFO))) and ($SELECT) group by h.id) as id;"
    gl0=$(psql $DB -tc "$SQLCMD"|grep -Eo "[0-9]+" |head -n1)
    echo " gl0>$gl0:=$SQLCMD"
    if [ $gl0 -gt $inv0 ]; then
      let pay0="$gl0-$inv0"
      rmd0=0
    else
      pay0=0
      let rmd0="$inv0-$gl0"
    fi
    echo "pay0>$pay0:=$gl0-$inv0"
    let inv1="$inv-$inv0"
    echo "inv1>$inv1:=$inv-$inv0"
    let gl1="$gl-$gl0"
    echo " gl1>$gl1:=$gl-$gl0"
    if [ $gl1 -gt $inv1 ]; then
      let pay1="$gl1-$inv1-$rmd0"
      rmd1=0
    else
      pay1=0
      let rmd1="$inv1-$gl1"
    fi
    echo "pay1>$pay1:=$gl1-$inv1-$rmd0"
    if [ -z "$1" ]; then
      echo -e "\e[1mTotal=$gl; invoices:($inv-$inv0)=$inv1; payments:($pay-$pay0)=$pay1\e[0m"
    else
      echo -e "\e[1mCompany=$1 >>>Total=$gl; invoices:($inv-$inv0)=$inv1; payments:($pay-$pay0)=$pay1\e[0m"
    fi
}

echo "Show invoice and account moves (include invoices)"
show_tot
if [ -n "$COMPANIES" ]; then
  for company_id in $COMPANIES;do
    show_tot $company_id
  done
fi

