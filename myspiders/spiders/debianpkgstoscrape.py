# use scrapy to generate a list of packages in 
# Debian GNU/Linux stable version

import scrapy, sqlite3

class DebianSpider(scrapy.Spider):
	name = 'debianpackages'
	
	def  start_requests(self):
		urls = [
			"https://packages.debian.org/stable/allpackages"
		]
		
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)
			
	def parse(self, response):
		conn = self.create_connection('debianpkgs.db')
		c = conn.cursor()
		
		# create table if not exists
		c.execute(
			'''
			CREATE TABLE IF NOT EXISTS packages (
			packageid int primary key not null,
			name text,
			link text,
			version text
			)
			'''
		)
		
		# query for insertion
		insert_query = ''' INSERT INTO packages(packageid, name, link, version) VALUES(?, ?, ?, ?) '''
		
		pkg_id = 0
		for package in response.css('dt'):
			pkg_id += 1
			pkg_name = package.css('a::text').get()
			pkg_link = 'https://packages.debian.org/stable/'+str(package.css('a').attrib['href'])
			pkg_version = str(package.xpath('./text()').get()).strip()
			# execute insertion
			c.execute(insert_query, (pkg_id, pkg_name, pkg_link, pkg_version))
			# scrapy iterator
			yield {
				'name': pkg_name,
				'link': pkg_link,
				'version': pkg_version
			}
			
		conn.commit()
		conn.close()
		
	def create_connection(self, db_file):
		try:
			conn = sqlite3.connect(db_file)
			return conn
		except Error as e:
			print(e)
 
		return None