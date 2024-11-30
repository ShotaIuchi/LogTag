FROM python:3.11-slim

COPY work /root/work
WORKDIR /root/work/tmp/
RUN pip install -e .

WORKDIR /root/work/log

RUN cp -a ../.logtag1 .logtag

RUN logtag *.txt --out ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-none.log > result-pwd-out-none

RUN logtag *.txt --merge --out ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-none-merge.log > result-home-none-merge

RUN logtag *.txt --sort --out ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-sort.log > result-pwd-out-sort

RUN logtag *.txt --sort --merge --out ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-sort-merge.log > result-home-sort-merge

RUN logtag *.txt --filter --out ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-filter.log > result-pwd-out-filter

RUN logtag *.txt --stop-first-tag --out ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-stop-first-tag.log > result-pwd-out-stop-first-tag

RUN logtag *.txt --stop-first-category --out ./tmp.log
RUN diff ./tmp.log ../correct/correct-single-stop-first-category.log > result-pwd-out-stop-first-category