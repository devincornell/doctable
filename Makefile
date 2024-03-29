
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

reinstall:
	pip uninstall -y doctable
	pip install .

uninstall:
	pip uninstall -y doctable

install:
	pip install .

################################# CREATE DOCUMENTATION ##############################

docs: pdoc example_html
	git add README.md

DOCS_FOLDER = docs/
EXAMPLES_FOLDER = examples/
DOCS_EXAMPLES_FOLDER = $(DOCS_FOLDER)/examples/

LEGACY_EXAMPLES_FOLDER = legacy/examples/
LEGACY_DOCS_EXAMPLES_FOLDER = $(DOCS_FOLDER)/legacy_examples/

example_html:
	jupyter nbconvert --to html $(EXAMPLES_FOLDER)/*.ipynb
	mv $(EXAMPLES_FOLDER)/*.html $(DOCS_EXAMPLES_FOLDER)
	git add --all $(DOCS_EXAMPLES_FOLDER)*.html

	jupyter nbconvert --to html $(LEGACY_EXAMPLES_FOLDER)/*.ipynb
	mv $(LEGACY_EXAMPLES_FOLDER)/*.html $(LEGACY_DOCS_EXAMPLES_FOLDER)
	git add --all $(LEGACY_DOCS_EXAMPLES_FOLDER)*.html


DOCS_REF_FOLDER = $(DOCS_FOLDER)/ref/
LEGACY_DOCS_REF_FOLDER = $(DOCS_FOLDER)/ref_legacy/
#pydoc -w doctable.ConnectEngine doctable.DocTable doctable.dbutils doctable.DocTableRows doctable.schemas.field_columns doctable.parse.pipeline doctable.parse.parsetree doctable.parse.parsefuncs doctable.Bootstrap doctable.Timer doctable.FSStore doctable.util.io
#mv *.html $(DOCS_REF_FOLDER)
pdoc:
	pdoc --docformat google -o ./docs/ref ./doctable/
	git add --all $(DOCS_REF_FOLDER)*.html

	pdoc --docformat google -o ./docs/ref_legacy ./legacy/doctable/
	git add --all ./docs/ref_legacy/*.html

clean_docs:
	-rm $(DOCS_REF_FOLDER)*.html
	-rm $(DOCS_EXAMPLES_FOLDER)*.html
	-rm $(LEGACY_DOCS_EXAMPLES_FOLDER)*.html


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


	
