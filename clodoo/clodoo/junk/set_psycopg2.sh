pkg=$(pip show psycopg2 2>/dev/null)
if [ -n "$pkg" ]; then
  for pkg in psycopg2-binary psycopg2; do
    pip uninstall $pkg
  done
  pip install psycopg2-binary
else
  echo "psycopg2 package is Ok"
fi
