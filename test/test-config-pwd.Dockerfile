FROM python:3.11-slim

COPY work /root/work
WORKDIR /root/work/tmp/
RUN pip install -e .

WORKDIR /root/work/log

RUN cp -a ../.logtag1 .logtag

RUN logtag *.txt > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-none.log > result-pwd-none

RUN logtag *.txt --sort > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-sort.log > result-pwd-sort

RUN logtag *.txt --filter > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-filter.log > result-pwd-filter

RUN logtag *.txt --stop-first-tag > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-stop-first-tag.log > result-pwd-stop-first-tag

RUN logtag *.txt --stop-first-category > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-stop-first-category.log > result-pwd-stop-first-category
