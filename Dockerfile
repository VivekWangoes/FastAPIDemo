# 
FROM python:3.9

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip3 install requests
RUN pip3 install httpx-oauth
RUN pip3 install python-dotenv

# 
COPY . /code

# 
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8095"]