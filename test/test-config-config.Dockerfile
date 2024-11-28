FROM python:3.11-slim

COPY work /root/work
WORKDIR /root/work/tmp/
RUN pip install -e .

WORKDIR /root/work/log

RUN logtag *.txt --config ../.logtag3 > ./tmp.log
RUN diff ./tmp.log ../correct/correct-config-column.log > result-config-column

RUN logtag *.txt --config ../.logtag4 > ./tmp.log
RUN diff ./tmp.log ../correct/correct-config-category-tag2.log > result-config-category

RUN logtag *.txt --config ../.logtag1 --category tag2 > ./tmp.log
RUN diff ./tmp.log ../correct/correct-config-category-tag2.log > result-config-category-category-add-tag

RUN logtag *.txt --config ../.logtag4 --category tag1 > ./tmp.log
RUN diff ./tmp.log ../correct/correct-config-category-tag1.log > result-config-category-category-override-tag
