FROM python:3.11-slim

COPY work /root/work
WORKDIR /root/work/tmp/
RUN pip install -e .

WORKDIR /root/work/log

RUN cp -a ../.logtag1 .logtag
RUN logtag * --filter > ./tmp.log
RUN diff ./tmp.log ../correct/correct5.log > result5