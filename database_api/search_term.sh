#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 \"search term\""
    exit 1
fi

SEARCH_TERM="$1"

psql english_exams -v search_term="'$SEARCH_TERM'" -f text_search.sql
