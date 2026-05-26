#!/bin/bash

celery -A planner worker --loglevel=info -f logs/celery.log