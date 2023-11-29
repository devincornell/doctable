PACKAGE_NAME = coproc
PACKAGE_FOLDER = $(PACKAGE_NAME)/

# PDOC_TARGET_FOLDER = ./site/api/ # pdoc html files will be placed here

TESTS_FOLDER = ./tests/ # all pytest files are here

EXAMPLE_NOTEBOOK_FOLDER = ./examples/# this is where example notebooks are stored
EXAMPLE_NOTEBOOK_MARKDOWN_FOLDER = ./docs/documentation/# this is where example notebooks are stored
# EXAMPLE_NOTEBOOK_HTML_FOLDER = ./site/example_notebooks/# this is where example notebooks are stored

LEGACY_NOTEBOOK_FOLDER = ./legacy/examples/
LEGACY_NOTEBOOK_MARKDOWN_FOLDER = ./docs/legacy_documentation/
#LEGACY_DOCS_EXAMPLES_FOLDER = $(DOCS_FOLDER)/legacy_examples/

REQUIREMENTS_FOLDER = ./requirements/

# examples
# make docs (generates all docs)
# make clean (deletes all doc files)
# make test (runs unit tests in tests/ and exports notebooks in examples/ and tries to run them)
# make build (actually builds the python package)
# make deploy (actually builds package)


#################### TO DEPLOY INSTRUCTIONS ###########################
#make test
#make clean
#make docs
#make build
#make deploy

# toplevel (run when enters 'make' without args)
all: docs build
	git add Makefile

final_check: docs build test
	@echo "ran final check"

push_all: 
	git commit -a -m '[auto_pushed_from_Makefile]'
	git push

reinstall: uninstall install
	@echo "reinstalled"

uninstall:
	pip uninstall -y $(PACKAGE_NAME)

install:
	pip install .

################################# CREATE DOCUMENTATION ##############################


docs: mkdocs requirements
	git add -f --all site/*
	git add --all docs/*

# for testing mkdocs
serve_mkdocs: mkdocs
	mkdocs serve -a localhost:8882

mkdocs: example_notebooks
	cp README.md docs/index.md
	mkdocs build
	mkdocs gh-deploy

#pdoc:
	# -mkdir $(PDOC_TARGET_FOLDER)
	# pdoc --docformat google -o $(PDOC_TARGET_FOLDER) $(PACKAGE_FOLDER)

# pdoc:
	# pdoc --docformat google -o ./docs/ref ./doctable/
	# git add --all $(DOCS_REF_FOLDER)*.html

	# pdoc --docformat google -o ./docs/ref_legacy ./legacy/doctable/
	# git add --all ./docs/ref_legacy/*.html

example_notebooks:
	-mkdir $(EXAMPLE_NOTEBOOK_MARKDOWN_FOLDER)
	jupyter nbconvert --to markdown $(EXAMPLE_NOTEBOOK_FOLDER)/*.ipynb
	mv $(EXAMPLE_NOTEBOOK_FOLDER)/*.md $(EXAMPLE_NOTEBOOK_MARKDOWN_FOLDER)

	-mkdir $(LEGACY_NOTEBOOK_MARKDOWN_FOLDER)
	jupyter nbconvert --to markdown $(LEGACY_NOTEBOOK_FOLDER)/*.ipynb
	mv $(LEGACY_NOTEBOOK_FOLDER)/*.md $(LEGACY_NOTEBOOK_MARKDOWN_FOLDER)

requirements:
	-mkdir $(REQUIREMENTS_FOLDER)
	pip freeze > $(REQUIREMENTS_FOLDER)/requirements.txt	
	pip list > $(REQUIREMENTS_FOLDER)/packages.txt

add_docs:
	git add $(REQUIREMENTS_FOLDER)/requirements.txt
	git add $(REQUIREMENTS_FOLDER)/packages.txt
	# git add --all $(PDOC_TARGET_FOLDER)
	# git add --all $(EXAMPLE_NOTEBOOK_HTML_FOLDER)
	git add --all $(EXAMPLE_NOTEBOOK_MARKDOWN_FOLDER)
	git add --all $(LEGACY_NOTEBOOK_MARKDOWN_FOLDER)

clean_docs:
	# -rm -r $(PDOC_TARGET_FOLDER)
	# -rm -r $(EXAMPLE_NOTEBOOK_HTML_FOLDER)
	-rm -r $(EXAMPLE_NOTEBOOK_MARKDOWN_FOLDER)/*.md
	-rm -r $(LEGACY_NOTEBOOK_MARKDOWN_FOLDER)/*.md

######################################## RUN TESTS ########################################

#TESTS_FOLDER = tests/
TESTS_FOLDER = tests/
pytest: uninstall
	# tests from tests folder
	cd $(TESTS_FOLDER); pytest test_*.py

TMP_TEST_FOLDER = tmp_test_deleteme
test_examples: uninstall
	# make temporary testing folder and copy files into it
	-rm -r $(TMP_TEST_FOLDER)
	mkdir $(TMP_TEST_FOLDER)
	cp $(EXAMPLES_FOLDER)/*.ipynb $(TMP_TEST_FOLDER)
	-cp $(EXAMPLES_FOLDER)/*.py $(TMP_TEST_FOLDER)
	
	# convert notebooks to .py scripts
	jupyter nbconvert --to script $(TMP_TEST_FOLDER)/*.ipynb
	
	# execute example files to make sure they work

	# main tutorials
	cd $(TMP_TEST_FOLDER); python ex_basics.py
	#cd $(TMP_TEST_FOLDER); python doctable_schema.py

	# cleanup temp folder
	-rm -r $(TMP_TEST_FOLDER)

test_commands: uninstall
	# test command line interface
	python -m doctable execute ":memory:" --docs "c.inspect_table_names()"
	python -m doctable execute ":memory:" "c.inspect_table_names()"

test: pytest test_examples test_commands
tests: test # alias	

	
clean_tests:
	-rm $(EXAMPLES_FOLDER)*.db
	-rm $(EXAMPLES_FOLDER)/exdb/*.db
	-rm $(TESTS_FOLDER)*.db
	-rm *.db
	
########################################## BUILD AND DEPLOY ################################

build:
	# install latest version of compiler software
	pip install --user --upgrade setuptools wheel
	
	# actually set up package
	python setup.py sdist bdist_wheel
	
	git add setup.cfg setup.py LICENSE.txt 
	
	
deploy: build
	# mostly pulled from https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56
	#also this: https://packaging.python.org/tutorials/packaging-projects/
	
	# first make sure deploy package is activated
	pip install --user --upgrade twine
	
	# create a source distribution
	python setup.py sdist
	
	# here we go now upload
	python -m twine upload dist/*
	
clean_deploy:
	-rm -r $(PACKAGE_NAME).egg-info
	-rm -r dist
	-rm -r build
	
################################ CLEAN ####################################

clean: clean_tests clean_docs clean_deploy


	
