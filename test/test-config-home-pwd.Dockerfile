FROM python:3.11-slim

COPY work /root/work
WORKDIR /root/work/tmp/
RUN pip install -e .

WORKDIR /root/work/log

RUN cp -a ../.logtag1 ~/.logtag
RUN cp -a ../.logtag2 .logtag

RUN logtag * > ./tmp.log
RUN diff ./tmp.log ../correct/correct-double-none.log > result-home-pwd-none

RUN logtag * --sort > ./tmp.log
RUN diff ./tmp.log ../correct/correct-double-sort.log > result-home-pwd-sort
