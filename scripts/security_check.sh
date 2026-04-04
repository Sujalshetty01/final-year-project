#!/bin/bash
set -e
# Python dependencies
safety check || true
# Node dependencies
cd frontend && npm audit || true
