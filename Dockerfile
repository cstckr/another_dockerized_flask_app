FROM python:3.9.12-alpine
WORKDIR /app
ADD . /app

RUN apk update
RUN apk add unixodbc libpq-dev gcc g++ unixodbc-dev gnupg
RUN wget https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/msodbcsql17_17.10.1.1-1_amd64.apk  && \
    wget https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/mssql-tools_17.10.1.1-1_amd64.apk  && \
    apk add --allow-untrusted msodbcsql17_17.10.1.1-1_amd64.apk && \
    apk add --allow-untrusted mssql-tools_17.10.1.1-1_amd64.apk
RUN pip install -r requirements.txt

EXPOSE 80

CMD ["python", "app.py"]