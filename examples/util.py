import urllib.request
def download_nss(
	baseurl='https://raw.githubusercontent.com/devincornell/nssdocs/master/docs/',
	years = (1987, 1988, 1990, 1991, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2002, 2006, 2010, 2015, 2017)
	):
	def read_url(url):
		return urllib.request.urlopen(url).read().decode('utf-8')
	
	ftemp = baseurl+'{}.txt'
	all_texts = [read_url(ftemp.format(year)) for year in years]
	return {yr:text for yr,text in zip(years,all_texts)}