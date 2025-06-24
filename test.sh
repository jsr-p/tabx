#!/usr/bin/env bash

# python >= 3.12
git checkout main
uv sync
pytest

# python == 3.11
git checkout py-311
uv sync
pytest
