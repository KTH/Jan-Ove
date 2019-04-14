#!/bin/sh
pipenv run green -vv --run-coverage --failfast "test" "$@"