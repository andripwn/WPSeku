"""Support for discovering Wordpress versions."""
from re import findall

from lib.request import *
from lib.wpscan_api import lookup


class wpversion(Request):
	def __init__(self,url,data,kwargs):
		self.url = url 
		self.data = data
		self.kwargs = kwargs
		Request.__init__(self,kwargs)

	def run(self):
		if self.kwargs['verbose'] is True:
			info('Checking WordPress version...')
		try:
			url = Path(self.url,'/wp-links-opml.php')
			resp = self.send(url=url,method="GET")
			if resp.status_code == 200 and resp.content != ("" or None):
				version = findall(decode('\S+WordPress/(\d+.\d+[.\d+]*)'),resp.content)
				if version:
					plus('Running WordPress version: %s'%version[0].decode('utf-8'))
					self.dbwpscan(version)
		except Exception as e:
			try:
				url = Path(self.url,'feed')
				resp = self.send(url=url,method="GET")
				if resp.status_code == 200 and resp.content != ("" or None):
					version = findall(decode('\S+?v=(\d+.\d+[.\d+]*)'),resp.content)
					if version:
						plus('Running WordPress version: %s'%version[0].decode('utf-8'))
						self.dbwpscan(version)
			except Exception as e:
				try:
					url = Path(self.url,'/feed/atom')
					resp = self.send(url=url,method="GET")
					if resp.status_code == 200 and resp.content != ("" or None):
						version = findall(decode('<generator uri="http://wordpress.org/" version="(\d+\.\d+[\.\d+]*)"'),resp.content)
						if version:
							plus('Running WordPress version: %s'%version[0].decode('utf-8'))
							self.dbwpscan(version)
				except Exception as e:
					try:
						url = Path(self.url,'/readme.html')
						resp = self.send(url=url,method="GET")
						if resp.status_code == 200 and resp.content != ("" or None):
							version = findall(decode('.*wordpress-logo.png" /></a>\n.*<br />.* (\d+\.\d+[\.\d+]*)\n</h1>'),resp.content)
							if version:
								plus('Running WordPress version: %s'%version[0].decode('utf-8'))
								self.dbwpscan(version)
					except Exception as e:
						try:
							url = Path(self.url,'')
							resp = self.send(url=url,method="GET")
							if resp.status_code == 200 and resp.content != ("" or None):
								version = findall(decode('<meta name="generator" content="WordPress (\d+\.\d+[\.\d+]*)"'),resp.content)
								if version:
									plus('Running WordPress version: %s'%version[0].decode('utf-8'))
									self.dbwpscan(version)
						except Exception:
							pass
	def dbwpscan(self,version):
		version = version[0].decode('utf-8')
		if not self.kwargs.get('api_token'):
			return
		entry = lookup('wordpresses', version.replace('.', ''), self.kwargs, version)
		if entry is None:
			return
		if entry.get('release_date'):
			more('Release date: %s' % entry['release_date'])
		vulnerabilities = entry.get('vulnerabilities') or []
		if not vulnerabilities:
			more('Not found vulnerabilities')
		for vulnerability in vulnerabilities:
			more('Title: %s' % vulnerability.get('title', 'Unknown'))
			for reference in (vulnerability.get('references') or {}).get('url') or []:
				more('Reference: %s' % reference)
			more('Fixed in: %s' % vulnerability.get('fixed_in', 'Unknown'))

	def version(self,version):
		vers = ""
		version = version[0].decode('utf-8')	
		for v in range(len(version.split('.'))):
			vers += version.split('.')[v]
		return vers
