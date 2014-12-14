#!/bin/bash

wget http://hal3.name/tmp/kaggle-wikipedia.tar.bz2
rm -rf wikipedia
tar -jxvf kaggle-wikipedia.tar.bz2
rm -rf kaggle-wikipedia.tar.bz2
