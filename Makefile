
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
	@echo "running final check"


PACKAGE_NAME = doctable
PACKAGE_FOLDER = $(PACKAGE_NAME)/



EXAMPLES_FOLDER = examples/
TESTS_FOLDER = tests/

DOCS_FOLDER = docs/
docs: example_html pydoc
	git add README.md


DOCS_EXAMPLES_FOLDER = $(DOCS_FOLDER)/examples/
example_html:
	#jupyter nbconvert --to markdown $(EXAMPLES_FOLDER)/*.ipynb
	#mv $(EXAMPLES_FOLDER)/*.md $(DOCS_FOLDER)
	jupyter nbconvert --to html $(EXAMPLES_FOLDER)/*.ipynb
	mv $(EXAMPLES_FOLDER)/*.html $(DOCS_EXAMPLES_FOLDER)
	git add --all $(DOCS_EXAMPLES_FOLDER)*.html

# use pydoc to generate documentation
DOCS_REF_FOLDER = $(DOCS_FOLDER)/ref/
pydoc:
	pydoc -w doctable.DocTable doctable.DocTable2 doctable.DocParser doctable.ParseTree doctable.ParseNode doctable.DocBootstrap
	mv *.html $(DOCS_REF_FOLDER)
	git add --all $(DOCS_REF_FOLDER)*.html


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

pytest:
	# tests from tests folder
	pytest $(TESTS_FOLDER)/test_dt1_*.py
	pytest $(TESTS_FOLDER)/test_dt2_*.py


TMP_TEST_FOLDER = tmp_test_deleteme
test: pytest
	
	# make temporary testing folder and copy files into it
	-rm -r $(TMP_TEST_FOLDER)
	mkdir $(TMP_TEST_FOLDER)
	cp $(EXAMPLES_FOLDER)/*.ipynb $(TMP_TEST_FOLDER)
	cp $(EXAMPLES_FOLDER)/*.py $(TMP_TEST_FOLDER)
	
	# convert notebooks to .py scripts
	jupyter nbconvert --to script $(TMP_TEST_FOLDER)/*.ipynb
	
	# run regular python
	cd $(TMP_TEST_FOLDER); python ./*.py
	
	# cleanup temp folder
	rm -r $(TMP_TEST_FOLDER)
	

clean:
	# leftover files from experimentation
	-rm $(EXAMPLES_FOLDER)*.db
	-rm $(TESTS_FOLDER)*.db
	
	# from building documents
	-rm $(DOCS_FOLDER)/*.md
	-rm $(DOCS_FOLDER)/*.html
	
	# from building python package
	-rm -r $(PACKAGE_NAME).egg-info
	-rm -r dist
	-rm -r build
	
