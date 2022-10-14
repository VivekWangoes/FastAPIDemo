# 
FROM python:3.9

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip3 install requests
<<<<<<< HEAD
RUN pip install httpx-oauth
RUN pip3 install python-dotenv
RUN pip3 install 'fastapi-users[sqlalchemy,oauth]'
=======
RUN pip3 install httpx-oauth
RUN pip3 install python-dotenv
>>>>>>> 02f341936e54e537fe3b7c5b3ef308a7500e35ba

# 
COPY . /code

# 
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8095"]