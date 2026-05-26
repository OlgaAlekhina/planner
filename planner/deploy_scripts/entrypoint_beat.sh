#!/bin/bash

celery -A planner beat --loglevel=info -f logs/celery.log