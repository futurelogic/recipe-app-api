#!/bin/bash
# USAGE:
#     for docker-compose.yml
#         command: {celery|sleeper}
gunicorn --preload -b:8001 
