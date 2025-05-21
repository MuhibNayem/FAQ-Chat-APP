#!/bin/bash

poetry run gunicorn -k uvicorn.workers.UvicornWorker \
         --bind 0.0.0.0:6969 \
         --workers 100 \
         src.main:app
