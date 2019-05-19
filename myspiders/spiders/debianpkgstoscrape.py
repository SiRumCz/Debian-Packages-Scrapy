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
			pkg_id += 1
			pkg_name = package.css('a::text').get()
			pkg_link = 'https://packages.debian.org/stable/'+str(package.css('a').attrib['href'])
			pkg_link = response.urljoin(pkg_link)
			# execute insertion
			# c.execute(insert_query, (pkg_id, pkg_name, pkg_link))

			yield scrapy.Request(
				url=pkg_link, 
				callback=self.pkg_links_parse,
				dont_filter=True,
				meta={'pkg_id': pkg_id, 'pkg_name': pkg_name}
			)
		
	# yield Request from packages.debian.org
	def pkg_links_parse(self, response):
		tracker_link = str(response.xpath('//li/a[contains(text(),\'Developer Information\')]/@href').get(default=None)).strip()
		metaparse = response.meta
		metaparse['tracker_link'] = tracker_link

		yield scrapy.Request(
			url=tracker_link, 
			callback=self.vcs_links_parse,
			dont_filter=True,
			meta=metaparse
		)

	# yield Request from tracker.debian.org/pkg
	def vcs_links_parse(self, response):
		vcs_link = str(response.xpath('//span/b[contains(text(), \'VCS:\')]/../following-sibling::a[1]/@href').get(default=None)).strip()

		pkg_item = items.Package()
		pkg_item['packageid'] = response.meta['pkg_id']
		pkg_item['name'] = response.meta['pkg_name']
		pkg_item['trackerlink'] =response.meta['tracker_link']
		pkg_item['vcslink'] = vcs_link

		yield pkg_item