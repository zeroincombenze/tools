echo cd $PWD
echo pytest
pytest
echo -e "\n\n\n\n"
echo pytest --cov=midea --cov-report=term-missing --cov-report=html
pytest --cov=midea --cov-report=term-missing --cov-report=html
echo -e "\n\n\n\n"
echo tox
tox

