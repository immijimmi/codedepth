:: Requires pytest and coverage to be installed
:: This script will run any test files it discovers in the directory and provide a breakdown of code coverage

cd ..
coverage run -m --source=. --omit="test\*,setup.py" py.test -v
coverage report

pause
