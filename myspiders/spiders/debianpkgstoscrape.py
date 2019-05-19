# Author: Chen, Zhe
# Email: zkchen@uvic.ca
#
# use scrapy to generate a list of packages in Debian GNU/Linux stable version
# scrape items include:
# package name, link in tracker.debian.org/pkg, VCS(Version Control Systems) link, version

import scrapy
from .. import items

class DebianSpider(scrapy.Spider):
	name = 'debianpackages'

	def  start_requests(self):
		urls = [
			"https://packages.debian.org/stable/allpackages"
		]
		
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	# initial scrapy parse	
	def parse(self, response):
		pkg_id = 0
		for package in response.css('dt'):
			pkg_item = items.Package()
			pkg_item['name'] = package.css('a::text').get()			
			pkg_item['packageid'] = pkg_id
			pkg_item['trackerlink'] = None
			pkg_item['vcslink'] = None

			pkg_id += 1
			pkg_link = package.css('a').attrib['href']

			if pkg_link is not None:
				pkg_link  = 'https://packages.debian.org/stable/'+str(pkg_link)

				yield scrapy.Request(
					url=pkg_link, 
					callback=self.pkg_links_parse,
					dont_filter=True,
					meta={'pkg_item': pkg_item}
				)
			else:
				yield pkg_item
		
	# yield Request from packages.debian.org
	def pkg_links_parse(self, response):
		meta_item = response.meta['pkg_item']

		tracker_link = response.xpath('//li/a[contains(text(),\'Developer Information\')]/@href').get(default=None)
		
		if tracker_link is not None:
			tracker_link = str(tracker_link).strip()
			meta_item['trackerlink'] = tracker_link

			yield scrapy.Request(
				url=tracker_link, 
				callback=self.vcs_links_parse,
				dont_filter=True,
				meta={'pkg_item': meta_item}
			)
		else:
			yield meta_item

	# yield Request from tracker.debian.org/pkg
	def vcs_links_parse(self, response):
		meta_pkg_item = response.meta['pkg_item']

		# this only gets the first <a> element next to 'VCS' on tracker.debian.org, so the potential problem could be there is no VCS link but only a website for browse is available
		vcs_link = response.xpath('//span/b[contains(text(), \'VCS:\')]/../following-sibling::a[1]/@href').get(default=None)

		if vcs_link is not None:
			vcs_link = str(vcs_link).strip()
			meta_pkg_item['vcslink'] = vcs_link

		yield meta_pkg_item