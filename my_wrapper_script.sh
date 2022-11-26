#!/usr/bin/bash
python manage.py makemigrations && python manage.py migrate
python manage.py runserver 0.0.0.0:81 & python manage.py run_jobs & wait -n 
exit $?