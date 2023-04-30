#!/bin/bash
VERSION=0.0.1 # `git describe --tags --abbrev=0 | cut -c2-` 
echo Building ${VERSION}
docker build \
  --no-cache \
  -t jbl2024/cassandre:${VERSION} \
  -t jbl2024/cassandre:latest .