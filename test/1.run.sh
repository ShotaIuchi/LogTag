#!/bin/bash

rm -rf ./work/tmp/
mkdir -p ./work/tmp/LogTag

cp -r ../LogTag ./work/tmp/
cp -r ../setup.py ./work/tmp/

docker compose build 
docker compose up -d

# rm -rf out
# mkdir -p out/
# docker cp test1:/root/work/log/result ./out/result1
# docker cp test2:/root/work/log/result ./out/result2
# docker cp test3:/root/work/log/result ./out/result3
# docker cp test4:/root/work/log/result ./out/result4
# docker cp test5:/root/work/log/result ./out/result5
# docker cp test6:/root/work/log/result ./out/result6
# docker cp test7:/root/work/log/result ./out/result7
