# Postgres / odoo mapping
# Odoo 6.1 - 7.0 -> psql-9.5: 5435
# Odoo 7.0 - 10.0 -> psql-10: 5433
# Odoo 10.0 - 15.0 -> psql-12: 5434
# Odoo 16.0 - 19.0 -> psql-16: 5436
# Odoo 18-0 - 19.0 -> psql-18: 5432 *

echo "Postgresql 12.0 at port 5432 (default)"
echo alias psql-12='psql -p5434'
alias psql-12='psql -p5434'

echo "Postgresql 10.0 at port 5433"
echo alias psql-10='psql -p5433'
alias psql-10='psql -p5433'

# echo "Postgresql 14.0 at port 5434"
# echo alias psql-14='psql -p5434'
# alias psql-14='psql -p5434'

# echo "Postgresql 15.0 at port 5435"
# echo alias psql-16='psql -p5435'
# alias psql-16='psql -p5435'

echo "Postgresql 16.0 at port 5436"
echo alias psql-16='psql -p5436'
alias psql-16='psql -p5436'

echo "Postgresql 9.5 at port 5435"
echo alias psql-9.5='psql -p5435'
alias psql-9.5='psql -p5435'


