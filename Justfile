all:
    just lint
    just readme
    just sphinx

install:
    uv sync
    uv pip install -e /home/jsr-p/gh-repos/documentation-stuff/sphinx-autodoc2

lint:
    ruff format src
    ruff format tests
    ruff format examples

readme:
    # - output-dir doesn't work inside the py files
    # - relative paths starting from examples/ dir
    quarto render examples/tutorial.py --output-dir ../_output
    quarto render examples/showcase.py --output-dir ../_output
    # examples
    quarto render examples/desc_exp.py --output-dir ../_output
    quarto render examples/desc_simple.py --output-dir ../_output
    quarto render examples/models_example.py --output-dir ../_output
    quarto render examples/models_simple.py --output-dir ../_output
    quarto render examples/color.py --output-dir ../_output
    quarto render examples/misc.py --output-dir ../_output
    quarto render examples/great_tables.py --output-dir ../_output
    quarto render examples/booktabs1.py --output-dir ../_output
    quarto render examples/booktabs2.py --output-dir ../_output
    quarto render examples/ascii.py --output-dir ../_output
    quarto render examples/cli.qmd --output-dir ../_output
    quarto render README.qmd

sphinx: 
    cp README.md docs/source
    mkdir -p docs/source/figs
    # copy example images to docs
    cp figs/*.png docs/source/figs/
    cp figs/*.svg docs/source/figs/
    just sphinx-clean 
    just sphinx-build
    
sphinx-build:
    sphinx-build docs/source docs/build

sphinx-clean:
    sphinx-build -M clean docs/source docs/build
    rm docs/source/tabx.rst || true
    rm docs/source/modules.rst || true
    rm -rf docs/source/apidocs/ || true

coverage:
    uv run coverage run -m pytest
    uv run coverage report
    uv run coverage html
    coverage-badge -f -o figs/coverage.svg

pypi:
    rm dist/* || true
    uv build
    uv publish -t $(pass pypi-token) \
       --publish-url https://upload.pypi.org/legacy/

testpypi:
    rm dist/* 
    uv build
    uv publish -t $(pass testpypi-token) \
        --publish-url https://test.pypi.org/legacy/
