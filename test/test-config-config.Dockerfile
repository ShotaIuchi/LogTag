FROM python:3.11-slim

COPY work /root/work
WORKDIR /root/work/tmp/
RUN pip install -e .

WORKDIR /root/work/log

RUN logtag *.txt --config ../.logtag3 > ./tmp.log
RUN diff ./tmp.log ../correct/correct-config-column.log > result-config-column

RUN logtag *.txt --config ../.logtag4 > ./tmp.log
RUN diff ./tmp.log ../correct/correct-config-category.log > result-config-category
