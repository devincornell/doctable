
# examples
# make docs (generates all docs)
# make clean (deletes all doc files)

# toplevel (run when enters 'make' without args)
all: docs
	git add Makefile

DOCS_FOLDER = docs/
MD_FOLDER = examples/markdown/
EXAMPLES_FOLDER = examples/

docs: gen_markdown pydoc

gen_markdown:
	jupyter nbconvert --to markdown $(EXAMPLES_FOLDER)/*.ipynb
	mv examples/*.md $(MD_FOLDER)
	git add $(MD_FOLDER)/*.md

pydoc:
	pydoc -w doctable.DocTable2
	pydoc -w doctable.DocTable
	-mkdir docs
	mv doctable.DocTable.html $(DOCS_FOLDER)
	mv doctable.DocTable2.html $(DOCS_FOLDER)
	git add $(DOCS_FOLDER)/*.html

test:
	@echo "need to implement testing with pytest"

clean:
	-rm $(MD_FOLDER)*.md
	-rm $(EXAMPLES_FOLDER)*.db
	-rm -r $(DOCS_FOLDER)
	
