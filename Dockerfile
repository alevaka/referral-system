FROM python:3.11

WORKDIR /referral-system

COPY ./requirements.txt /referral-system/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /referral-system/requirements.txt

COPY ./ /referral-system/

RUN alembic upgrade head

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
