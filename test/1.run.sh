#!/bin/bash

rm -rf ./work/tmp/
mkdir -p ./work/tmp/LogTag

cp -r ../LogTag ./work/tmp/
cp -r ../setup.py ./work/tmp/

docker compose build 
docker compose up -d
