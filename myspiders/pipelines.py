# -*- coding: utf-8 -*-
#
# Author: Chen, Zhe 
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3

class MyspidersPipeline(object):

    def __init__(self):
        self.connection = sqlite3.connect('debianpkgs.db')
        self.cursor = self.connection.cursor()
        # create table if not exists
        self.cursor.execute(
		    '''
		    CREATE TABLE IF NOT EXISTS packages (
		    packageid int primary key not null,
		    name text,
		    trackerlink text,
		    vcslink text
		    )
		    '''
	    )
	    # delete any data from packages table
        self.cursor.execute(''' DELETE FROM packages ''')
        # query for insertion
        self.insert_query = ''' INSERT INTO packages(packageid, name, trackerlink, vcslink) VALUES(?, ?, ?, ?) '''

    def process_item(self, item, spider):
        self.cursor.execute(self.insert_query, (item['packageid'], item['name'], item['trackerlink'], item['vcslink']))

        return item

    def close_spider(self, spider):
        self.connection.commit()
        self.connection.close()