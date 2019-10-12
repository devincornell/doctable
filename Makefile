
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
DOCS_FOLDER = docs/
EXAMPLES_FOLDER = examples/
TESTS_FOLDER = tests/

docs: example_markdown pydoc
	git add README.md

example_markdown:
	jupyter nbconvert --to markdown $(EXAMPLES_FOLDER)/*.ipynb
	mv $(EXAMPLES_FOLDER)/*.md $(DOCS_FOLDER)
	git add $(DOCS_FOLDER)/*.md

# use pydoc to generate documentation
pydoc:
	pydoc -w doctable
	pydoc -w doctable.DocTable2
	pydoc -w doctable.DocTable
	
	mv doctable.html $(DOCS_FOLDER)
	mv doctable.DocTable.html $(DOCS_FOLDER)
	mv doctable.DocTable2.html $(DOCS_FOLDER)
	git add $(DOCS_FOLDER)/*.html

build:
	# install latest version of compile software
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

TMP_TEST_FOLDER = tmp_test_deleteme
test:
	# tests from tests folder
	#pytest $(TESTS_FOLDER)/test_dt1_*.py (THERE CURRENTLY ARE NO doctable1 TESTS HERE.)
	pytest $(TESTS_FOLDER)/test_dt2_*.py
	
	# make temporary testing folder and copy files into it
	-rm -r $(TMP_TEST_FOLDER)
	mkdir $(TMP_TEST_FOLDER)
	cp $(EXAMPLES_FOLDER)/*.ipynb $(TMP_TEST_FOLDER)
	cp $(EXAMPLES_FOLDER)/*.py $(TMP_TEST_FOLDER)
	
	# convert notebooks to .py scripts
	jupyter nbconvert --to script $(TMP_TEST_FOLDER)/*.ipynb
	
	
	# NOTE: THIS IS WEIRD BECAUSE PYTEST RELIES ON "test_" prefixes
	#     to both scripts and functions. SO THE OUTPUT WILL LOOK LIKE
	#     0 tests run AND WILL GIVE ERROR make: *** [test] Error 5.
	#     IF THERE IS A MISTAKE, IT WILL RAISE AN ERROR AND FAIL.
	# NOTE2: IT MAY BE DIFFICULT TO DEBUG BECAUSE YOU WILL NEED TO
	#     TRACE THE ERROR BACK TO THE ORIGINAL NOTEBOOK.
	
	# run tests
	# must cd into temp folder bc that's where example scripts
	#     are supposed to run
	#-cd $(TMP_TEST_FOLDER); pytest ./*.py
	
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
	
