FROM python:3.10.6

WORKDIR F:\work_python_pipenv\parse_html

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD [ "python", "./bot.py" ] 