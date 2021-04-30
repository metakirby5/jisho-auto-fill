#!/usr/bin/env bash

curl -G --data-urlencode "keyword=$*" "https://jisho.org/api/v1/search/words" | jq