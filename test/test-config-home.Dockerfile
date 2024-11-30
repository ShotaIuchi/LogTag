FROM python:3.11-slim

COPY work /root/work
WORKDIR /root/work/tmp/
RUN pip install -e .

WORKDIR /root/work/log

RUN cp -a ../.logtag1 ~/.logtag

RUN logtag *.txt > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-none.log > result-home-none

RUN logtag *.txt --merge > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-none-merge.log > result-home-none-merge

RUN logtag *.txt --sort > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-sort.log > result-home-sort

RUN logtag *.txt --sort --merge > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-sort-merge.log > result-home-sort-merge

RUN logtag *.txt --filter > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-filter.log > result-home-filter

RUN logtag *.txt --stop-first-tag > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-stop-first-tag.log > result-home-stop-first-tag

RUN logtag *.txt --stop-first-category > ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-stop-first-category.log > result-home-stop-first-category
