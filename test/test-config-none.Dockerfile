FROM python:3.11-slim

COPY work /root/work
WORKDIR /root/work/tmp/
RUN pip install -e .

WORKDIR /root/work/log

RUN logtag * > ./tmp.log
RUN diff ./tmp.log ../correct/correct-none-none.log > result-none-none

RUN logtag * --sort > ./tmp.log
RUN diff ./tmp.log ../correct/correct-none-sort.log > result-none-sort
