FROM python:3.11-slim

COPY work /root/work
WORKDIR /root/work/tmp/
RUN pip install -e .

WORKDIR /root/work/log

RUN logtag *.txt --config ../.logtag1 > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-none.log > result-user-none

RUN logtag *.txt --merge --config ../.logtag1 > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-none-merge.log > result-user-none-merge

RUN logtag *.txt --sort --config ../.logtag1 > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-sort.log > result-user-sort

RUN logtag *.txt --sort --merge --config ../.logtag1> ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-sort-merge.log > result-user-sort-merge

RUN logtag *.txt --filter --config ../.logtag1 > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-filter.log > result-user-filter

RUN logtag *.txt --stop-first-tag --config ../.logtag1 > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-stop-first-tag.log > result-user-stop-first-tag

RUN logtag *.txt --stop-first-category --config ../.logtag1 > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-stop-first-category.log > result-user-stop-first-category
