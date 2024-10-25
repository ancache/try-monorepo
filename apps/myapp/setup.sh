# pyenv install 3.13.0b1  # descope trying this with different python versions
poetry init
# poetry env use ~/.pyenv/versions/3.13.0b1/bin/python

# check if the following is necessary
poetry config --list
poetry config virtualenvs.in-project true  # lets vscode see the poetry env; workspace root repo must be the same as the poetry project root

# create venv and lock file
poetry install

poetry show # to see what we've installed

# add libraries; use editable flag if you are developing the library as well
poetry add -e ../../libraries/api-utils 
poetry add -e ../../libraries/processing-utils
# in case of errors, try removing the venv and possibly the poetry.lock file and running poetry install again
rm rf .venv  # or poetry env remove .venv
rm poetry.lock
# you might need to restart VSCode to see imports from the new libraries in green (i.e. with IDE support)

# add dev requirements
poetry add pytest --group dev
poetry add black --group dev

poetry show  # to see what we've installed now

poetry run python main.py