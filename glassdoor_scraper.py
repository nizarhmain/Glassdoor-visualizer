from lxml import html, etree
import requests
import re
import os
import sys
import unicodecsv as csv
import argparse
import json


def parse(keyword, place, iteration):
		job_listings = []
		for x in range(0, iteration):
			headers = {	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
				'accept-encoding': 'gzip, deflate, sdch, br',
				'accept-language': 'en-GB,en-US;q=0.8,en;q=0.6',
				'referer': 'https://www.glassdoor.com/',
				'upgrade-insecure-requests': '1',
				'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
				'Cache-Control': 'no-cache',
				'Connection': 'keep-alive'
				}
			job_litsting_url = 'https://www.glassdoor.com/Job/denmark-software-jobs-SRCH_IL.0,7_IN63_KO8,16_IP'+ str(x) +'.htm'
			print(job_litsting_url)
			
			response = requests.post(job_litsting_url, headers=headers)

			parser = html.fromstring(response.text)
			# Making absolute url
			base_url = "https://www.glassdoor.com"
			parser.make_links_absolute(base_url)

			XPATH_ALL_JOB = '//li[@class="jl"]'
			XPATH_NAME = './/a/text()'
			XPATH_JOB_URL = './/a/@href'
			XPATH_LOC = './/span[@class="subtle loc"]/text()'
			XPATH_COMPANY = './/div[@class="flexbox empLoc"]/div/text()'
			XPATH_SALARY = './/span[@class="green small"]/text()'

			listings = parser.xpath(XPATH_ALL_JOB)
			for job in listings:
				raw_job_name = job.xpath(XPATH_NAME)
				raw_job_url = job.xpath(XPATH_JOB_URL)
				raw_lob_loc = job.xpath(XPATH_LOC)
				raw_company = job.xpath(XPATH_COMPANY)
				raw_salary = job.xpath(XPATH_SALARY)

				# Cleaning data
				job_name = ''.join(raw_job_name).strip(
					'–') if raw_job_name else None
				job_location = ''.join(raw_lob_loc) if raw_lob_loc else None
				raw_state = re.findall(",\s?(.*)\s?", job_location)
				state = ''.join(raw_state).strip()
				raw_city = job_location.replace(state, '')
				city = raw_city.replace(',', '').strip()
				company = ''.join(raw_company).replace('–', '')
				salary = ''.join(raw_salary).strip()
				job_url = raw_job_url[0] if raw_job_url else None

				jobs = {
					"Name": job_name,
					"Company": company,
					"State": place,
					"City": city,
					"Salary": salary,
					"Location": job_location,
					"Url": job_url
				}
				job_listings.append(jobs)

			# before i return the job listings i need to iterate more
		return job_listings


if __name__ == "__main__":

	''' eg-:python 1934_glassdoor.py "Android developer", "new york" '''

	argparser = argparse.ArgumentParser()
	argparser.add_argument('keyword', help='job name', type=str)
	argparser.add_argument('place', help='job location', type=str)
	args = argparser.parse_args()
	keyword = args.keyword
	place = args.place
	print("Fetching job details")
	scraped_data = parse(keyword, place, 29)		
	print("Writing data to output file")

	with open('%s-%s-job-results.csv' % (keyword, place), 'wb')as csvfile:
		fieldnames = ['Name', 'Company', 'State',
					  'City', 'Salary', 'Location', 'Url']
		writer = csv.DictWriter(
			csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
		writer.writeheader()
		if scraped_data:
			for data in scraped_data:
				writer.writerow(data)
		else:
			print("Your search for %s, in %s does not match any jobs" %
				  (keyword, place))
