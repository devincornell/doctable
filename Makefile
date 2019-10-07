
# toplevel (run when enters 'make' without args)
all: gen_markdown

MD_FOLDER = examples/markdown/
EXAMPLES_FOLDER = examples/
gen_markdown:
	jupyter nbconvert --to markdown $(EXAMPLES_FOLDER)/*.ipynb
	mv examples/*.md $(MD_FOLDER)
	git add $(MD_FOLDER)/*.md


clean:
	-rm $(MD_FOLDER)*.md
	-rm $(EXAMPLES_FOLDER)*.db
