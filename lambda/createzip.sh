#!/bin/bash
mkdir test
cp main.py requirements.txt test
cd test
pip3 install --target=./ -r requirements.txt
zip -r lambda.zip .
cd ..
mv test/lambda.zip .
rm -rf test