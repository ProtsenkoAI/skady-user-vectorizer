export PATH="$HOME/.local/bin:$PATH"
cd $HOME/Projects/skady-user-vectorizer/
printenv >> theenv.txt
pipenv run python3 ./schedule_main_runs.py
