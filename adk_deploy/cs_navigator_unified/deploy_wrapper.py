# -*- coding: utf-8 -*-
"""
Wrapper script to deploy with proper encoding
"""

import sys
import io
import os

# Force UTF-8 encoding for stdout/stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Set environment
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Change to agent directory
agent_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(agent_dir)

# Import and run the CLI
from google.adk.cli import main
import click

# Run the deploy command
sys.argv = [
    'adk',
    'deploy',
    'agent_engine',
    '--project=csnavigator-vertex-ai',
    '--region=us-central1',
    '--display_name=CS_Navigator_Unified',
    '.'
]

try:
    main.main(standalone_mode=False)
except click.exceptions.Exit as e:
    sys.exit(e.exit_code)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
