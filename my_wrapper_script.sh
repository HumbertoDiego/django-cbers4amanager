#!/bin/bash

# Start the first process
python manage.py runserver 0.0.0.0:81 &
  
# Start the second process
python manage.py run_jobs &
  
# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?