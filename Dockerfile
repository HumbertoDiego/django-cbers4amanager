FROM osgeo/gdal:ubuntu-small-3.3.3
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY .  /app
RUN apt update && apt install lsof nmap python3-pip python3-psycopg2 postgresql-client -y
RUN python -m pip install -r requirements.txt
#RUN python manage.py makemigrations && python manage.py migrate
#CMD ["python", "manage.py","runserver","0.0.0.0:81"]