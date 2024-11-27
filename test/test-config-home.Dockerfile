FROM python:3.11-slim

COPY work /root/work
WORKDIR /root/work/tmp/
RUN pip install -e .

WORKDIR /root/work/log

RUN cp -a ../.logtag1 ~/.logtag

RUN logtag * > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-none.log > result-home-none

RUN logtag * --sort > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-sort.log > result-home-sort

RUN logtag * --filter > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-filter.log > result-home-filter

RUN logtag * --stop-first-tag > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-stop-first-tag.log > result-home-stop-first-tag

RUN logtag * --stop-first-category > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-stop-first-category.log > result-home-stop-first-category
