
'''
this file automatically builds the index.html file for the doctable index page
it is typically called from the Makefile
basically just makes links for files in the docs folder
'''

from glob import glob
import os.path

docs_folder = 'docs/'
#github_branch = 'https://github.com/devincornell/doctable/blob/master/'


html_fnames = glob(docs_folder+'/*.html')

#md_fnames = glob(docs_folder+'/*.md')
#md_fnames = [github_branch+fn for fn in md_fnames]


output_html = '<h1>DocTable Python Package</h1>'

output_html += '<p>Check out the <a href="https://github.com/devincornell/doctable/blob/master/README.md">README file</a> of the repository for a description and examples of how to use doctable.</p>'

output_html += '<h2>Class Documentation Files</h2>'
for hfn in html_fnames:
	bn = os.path.basename(hfn)
	bn = '.'.join(bn.split('.')[:-1])
	output_html += '<a href="{}"><h3>{}</h3></a>'.format(hfn,bn)

with open(docs_folder+'/index.html','w') as f:
	f.write(output_html)
