echo "Run from within top of project dir"
echo "Assumes python and pip are installed"

python3 -m venv venv
. venv/bin/activate
pip install flask
pip install waitress
pip install requests
pip install psutil
