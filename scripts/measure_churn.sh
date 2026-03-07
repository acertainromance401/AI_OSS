#!/bin/bash
# 지난 주 동안의 Code Churn 계산

git log --since="1 week ago" --numstat --pretty=format:"" | \
awk '{
    added += $1;
    removed += $2
} END {
    print "Lines Added:", added
    print "Lines Removed:", removed
    print "Total Churn:", added + removed
}'
