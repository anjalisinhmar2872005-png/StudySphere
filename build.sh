#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python -c "import os,base64; open('/tmp/live_data.json','wb').write(base64.b64decode(os.environ['DATA_FIXTURE_B64']))"
python manage.py loaddata /tmp/live_data.json