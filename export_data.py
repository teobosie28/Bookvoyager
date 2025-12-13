#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to export database data to JSON file with proper UTF-8 encoding
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookvoyager.settings')
django.setup()

from django.core.management import call_command
from django.core import serializers
from io import StringIO

# Export data
output = StringIO()
call_command('dumpdata', stdout=output, format='json', indent=2)

# Write to file with UTF-8 encoding
with open('data.json', 'w', encoding='utf-8') as f:
    f.write(output.getvalue())

print("Data exported successfully to data.json")

