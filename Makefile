
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


################################# CREATE DOCUMENTATION ##############################

docs: example_html pydoc
	git add README.md

DOCS_FOLDER = docs/
EXAMPLES_FOLDER = examples/
DOCS_EXAMPLES_FOLDER = $(DOCS_FOLDER)/examples/
example_html:
	jupyter nbconvert --to html $(EXAMPLES_FOLDER)/*.ipynb
	
	mv $(EXAMPLES_FOLDER)/*.html $(DOCS_EXAMPLES_FOLDER)
	git add --all $(DOCS_EXAMPLES_FOLDER)*.html


DOCS_REF_FOLDER = $(DOCS_FOLDER)/ref/
pydoc:
	pydoc -w doctable.DocTableLegacy doctable.DocTable doctable.DocParser doctable.ParseTree doctable.ParseNode doctable.DocBootstrap doctable.Distribute doctable.parse
	mv *.html $(DOCS_REF_FOLDER)
	git add --all $(DOCS_REF_FOLDER)*.html

clean_docs:
	-rm $(DOCS_REF_FOLDER)*.html
	-rm $(DOCS_EXAMPLES_FOLDER)*.html


######################################## RUN TESTS ########################################

TESTS_FOLDER = tests/
pytest:
	# tests from tests folder
	pytest $(TESTS_FOLDER)/test_doctable_*.py
	pytest $(TESTS_FOLDER)/test_docparser_*.py
	pytest $(TESTS_FOLDER)/test_distribute*.py
	pytest $(TESTS_FOLDER)/test_legacy_*.py

TMP_TEST_FOLDER = tmp_test_deleteme
test_examples:
	# make temporary testing folder and copy files into it
	-rm -r $(TMP_TEST_FOLDER)
	mkdir $(TMP_TEST_FOLDER)
	cp $(EXAMPLES_FOLDER)/*.ipynb $(TMP_TEST_FOLDER)
	cp $(EXAMPLES_FOLDER)/*.py $(TMP_TEST_FOLDER)
	
	# convert notebooks to .py scripts
	jupyter nbconvert --to script $(TMP_TEST_FOLDER)/*.ipynb
	
	# run ipython so it will test out "%time " statements etc.
	cd $(TMP_TEST_FOLDER); ipython ./*.py
	
	# cleanup temp folder
	rm -r $(TMP_TEST_FOLDER)

test: pytest test_examples
	

	
clean_tests:
	-rm $(EXAMPLES_FOLDER)*.db
	-rm $(EXAMPLES_FOLDER)/exdb/*.db
	-rm $(TESTS_FOLDER)*.db
	-rm *.db
	
########################################## BUILD AND DEPLOY ################################

PACKAGE_NAME = doctable
PACKAGE_FOLDER = $(PACKAGE_NAME)/
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


	
