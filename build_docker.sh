#!/bin/bash
VERSION=`git describe --tags --abbrev=0 | cut -c2-` 
echo Building ${VERSION}
docker buildx build --platform=linux/amd64 \
  --no-cache \
  -t jbl2024/cassandre:${VERSION} \
  -t jbl2024/cassandre:latest .