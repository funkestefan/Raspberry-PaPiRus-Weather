#!/usr/bin/env bash

## get icons from openweathermap.org

for i in 01 02 03 04 09 10 11 13 50; do
  curl -O http://openweathermap.org/img/w/${i}d.png
  curl -O http://openweathermap.org/img/w/${i}d.png
done
