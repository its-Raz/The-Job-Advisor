import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from playwright.async_api import Error
import csv
import datetime
import pandas as pd
import glob
from ui import *

# Log In details for BRIGHT-DATA
username=''
password=''
auth=f'{username}:{password}'
host = 'brd.superproxy.io:9222'
browser_url = f'wss://{auth}@{host}'

# configure number of jobs to scrape from each site, default value is 10
link_jobs_num = 10
indeed_jobs_num = 10
zip_jobs_num = 10

# Current Time Stamp
current_date_and_time = datetime.datetime.now()
print("Current date and time:", current_date_and_time)

async def linkedin_scraping(keyword,j_location,job_number):
    """
        Asynchronously scrapes job listings from LinkedIn based on the provided keyword.

        Args:
        - keyword (str): The search keyword for job listings.
        - job_number (int): The maximum number of job listings to scrape.

        Returns:
        - None

        Utilizes Playwright to scrape job listings from LinkedIn, extracting details such as title, company name, location, etc.
        Saves the scraped data to a CSV file.

        Note:
        - This function requires Playwright library and Python 3.7+ for asynchronous operations.
        - Ensure 'browser_url' is defined before invoking this function.
        """
    def write_to_file(scraped_data):
        """
            Writes scraped job data to 'link_jobs.csv' in CSV format.

            Args:
            - scraped_data (list of dicts): List of dictionaries containing job data.

            Returns:
            - None

            Writes 'scraped_data' to a CSV file with specific fieldnames:
            'Title', 'Company_Name', 'Company_URL', 'Job_Location', 'Seniority_level',
            'Employment_type', 'Job_function', 'Industries', 'About', 'Job_URL',
            'Posted', and 'Collected'. Prints a message upon successful completion.

            Example:
            >>> write_to_file(scraped_data)
            """
        csv_file = 'link_jobs.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['Title', 'Company_Name', 'Company_URL', 'Job_Location',
                                                      'Seniority_level', 'Employment_type', 'Job_function',
                                                      'Industries', 'About','Job_URL','Posted','Collected'])
            writer.writeheader()
            writer.writerows(scraped_data)

            print(f"Scraped data saved to '{csv_file}'.")


    async with async_playwright() as pw:

        max_retries = 100
        print('connect')
        browser = await pw.chromium.connect_over_cdp(browser_url)
        print("connected")
        page = await browser.new_page()  # Open new page

        # Define the base URL for the job search
        base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

        # Define search parameters
        search_params = {
            'keywords': keyword,
            'location': j_location,
            'geoId': '103644278',
            'trk': 'public_jobs_jobs-search-bar_search-submit',
            'start': 25,  # Initial start value
            'original_referer': ''
        }

        max_pages = 25  # Maximum number of pages to scrape
        scraped_data = []
        index = 0

        for page_num in range(max_pages):
            if len(scraped_data) == job_number:
                print('reached max jobs needed!')
                break

            # Update the start parameter for each page
            search_params['start'] += 27

            url = f"{base_url}?{'&'.join([f'{key}={value}' for key, value in search_params.items()])}"
            print(url)

            # Retry navigating to the page for a certain number of times
            for retry_count in range(max_retries):
                try:
                    await page.goto(url, timeout=120000)  # Go to LinkedIn job search page
                    await page.wait_for_load_state('load')

                    # Check if the page contains job listings
                    if await page.query_selector('.job-search-card'):
                        print(f"Successfully reached search results page for page {page_num}.")
                        break  # Break out of the loop if successful
                    else:
                        print(f"Not on search results page for page {page_num}. Retrying...")
                except Error as pe:
                    print(f"Error occurred: {pe}")
                    if retry_count == 50 or retry_count > 60:
                        print("Trying to open new browser")
                        browser = await pw.chromium.connect_over_cdp(browser_url)
                        print("connected to new browser")
                        page = await browser.new_page()
                        print('open new page')
                    elif retry_count < max_retries - 1:
                        print(f"Retrying... Attempt {retry_count + 1}")


                    else:
                        print("Max retries exceeded. Exiting.")
                        await browser.close()
                        write_to_file(scraped_data=scraped_data)
                        return

            # Extract href attributes using Playwright
            html_content = await page.evaluate('()=>document.documentElement.outerHTML')

            # Parse the HTML with Beautiful Soup
            soup = BeautifulSoup(html_content, 'html.parser')
            job_listings = soup.find_all('div', {'class': 'job-search-card'})

            # Process job listings on the current page
            for job in job_listings:
                if len(scraped_data) == job_number:
                    print('reached max jobs needed!')
                    break


                try:
                    anchor_tag = job.find('a', class_='base-card__full-link')
                    href_link = anchor_tag['href']
                    for retry_count in range(max_retries):
                        try:
                            await page.goto(href_link, timeout=120000)
                            await page.wait_for_load_state('load')

                            if await page.query_selector('.top-card-layout__title'):
                                index += 1
                                print(f'Successfully reached job number {index} listing site')
                                html_content = await page.evaluate('()=>document.documentElement.outerHTML')
                                soup = BeautifulSoup(html_content, 'html.parser')
                                title = soup.find('h1', {'class': 'top-card-layout__title'}).text.strip()
                                company = soup.find('a', {'class': 'topcard__org-name-link'})
                                company_name = company.text.strip()
                                company_url = company['href']
                                location = soup.find('span',
                                                     {'class': 'topcard__flavor topcard__flavor--bullet'}).text.strip()
                                ul_element = soup.find('ul', class_='description__job-criteria-list')
                                time = soup.find('span', class_='posted-time-ago__text').text.strip()
                                job_crit = {}

                                # Check if the ul element is found
                                if ul_element:
                                    # Find all li elements under the ul element
                                    li_elements = ul_element.find_all('li')


                                    # Loop through each li element
                                    for li in li_elements:
                                        # Find the span element within the li
                                        span_element = li.find('span')
                                        h = li.find('h3')

                                        # Check if span element is found
                                        if span_element and h:
                                            # Extract and append the text of the span element
                                            job_crit[h.text.strip()]=(span_element.text.strip())
                                            print(h.text.strip())
                                            print(span_element.text.strip())
                                        else:
                                            print('no span or h')
                                            print(len(job_crit))
                                            job_crit['Job_function']='null'



                                about_element = soup.find('div', class_='show-more-less-html__markup')
                                about=''
                                if about_element:
                                    about = about_element.text.strip()
                                try:
                                    scraped_data.append(
                                        {'Title': title, 'Company_Name': company_name, 'Company_URL': company_url,
                                         'Job_Location': location, 'Seniority_level': job_crit['Seniority level'],
                                         'Employment_type': job_crit['Employment type'], 'Job_function': job_crit['Job function'],
                                         'Industries': job_crit['Industries'], 'About': about,'Job_URL':href_link,'Posted':time,'Collected':current_date_and_time})
                                    print(f"Title: {title}\nCompany: {company_name}\n")
                                    break
                                except Exception as e:
                                    print(f"exception!! {e}")
                            else:
                                print(f'Not reached job numer {index} site')
                        except Error as e:
                            print(f"Error when goto occurred: {e}")
                            if retry_count == 50 or retry_count > 60:
                                print("Trying to open new browser in job listing block")
                                browser = await pw.chromium.connect_over_cdp(browser_url)
                                print("connected to new browser")
                                page = await browser.new_page()
                                print('open new page')
                except Error as e:
                    print(f"Error occurred: {e}")
                    # Handle the error here if needed

        await browser.close()
        write_to_file(scraped_data=scraped_data)


async def indeed_scraping(keyword,j_location,job_number):
    """
        Asynchronously scrapes job listings from Indeed based on the provided keyword.

        Args:
        - keyword (str): The search keyword for job listings.
        - job_number (int): The maximum number of job listings to scrape.

        Returns:
        - None

        Utilizes Playwright to scrape job listings from Indeed, extracting details such as title, company name, location, etc.
        Saves the scraped data to a CSV file.

        Note:
        - This function requires Playwright library and Python 3.7+ for asynchronous operations.
        - Ensure 'browser_url' is defined before invoking this function.
        """
    def write_to_file(scraped_data):
        """
                    Writes scraped job data to 'indeed_jobs.csv' in CSV format.

                    Args:
                    - scraped_data (list of dicts): List of dictionaries containing job data.

                    Returns:
                    - None

                    Writes 'scraped_data' to a CSV file with specific fieldnames:
                    'Title', 'Company_Name', 'Company_URL', 'Job_Location', 'Seniority_level',
                    'Employment_type', 'Job_function', 'Industries', 'About', 'Job_URL',
                    'Posted', and 'Collected'. Prints a message upon successful completion.

                    Example:
                    >>> write_to_file(scraped_data)
                    """
        csv_file = 'indeed_jobs.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['Title', 'Company_Name', 'Company_URL', 'Job_Location',
                                                      'Seniority_level', 'Employment_type', 'Job_function',
                                                      'Industries', 'About','Job_URL','Posted','Collected'])
            writer.writeheader()
            writer.writerows(scraped_data)

            print(f"Scraped data saved to '{csv_file}'.")


    async with async_playwright() as pw:
        max_retries = 50
        print('connect')
        browser = await pw.chromium.connect_over_cdp(browser_url)
        print("connected")
        page = await browser.new_page()  # Open new page

        # Define the base URL for the job search
        base_url = f"https://www.indeed.com/jobs?q={keyword}&l={j_location}&start="

        # Define search parameters


        max_pages = 30  # Maximum number of pages to scrape
        scraped_data = []
        index = 0
        start=60
        for page_num in range(max_pages):
            if len(scraped_data) == job_number:
                print('reached max jobs needed!')
                break

            # Update the start parameter for each page
            start+=10

            url = f"{base_url}{start}"
            print(url)

            # Retry navigating to the page for a certain number of times
            for retry_count in range(max_retries):
                try:
                    await page.goto(url, timeout=120000)  # Go to LinkedIn job search page
                    await page.wait_for_load_state('load')
                    # html = await page.content()
                    # with open("output.txt", "w", encoding="utf-8") as file:
                    #     # Write your string/content to the file
                    #     file.write(html)
                    # return
                    # Check if the page contains job listings
                    if await page.query_selector('.jobTitle'):
                        print(f"Successfully reached search results page for page {page_num}.")
                        break  # Break out of the loop if successful
                    else:
                        print(f"Not on search results page for page {page_num}. Retrying...")
                        print("Trying to open new browser")
                        browser = await pw.chromium.connect_over_cdp(browser_url)
                        print("connected to new browser")
                        page = await browser.new_page()
                        print('open new page')
                except Error as pe:
                    print(f"Error occurred: {pe}")
                    if retry_count == 50 or retry_count == 70:
                        print("Trying to open new browser")
                        browser = await pw.chromium.connect_over_cdp(browser_url)
                        print("connected to new browser")
                        page = await browser.new_page()
                        print('open new page')
                    elif retry_count < max_retries - 1:
                        print(f"Retrying... Attempt {retry_count + 1}")


                    else:
                        print("Max retries exceeded. Exiting.")
                        await browser.close()
                        write_to_file(scraped_data=scraped_data)
                        return

            # Extract href attributes using Playwright
            html_content = await page.evaluate('()=>document.documentElement.outerHTML')

            # Parse the HTML with Beautiful Soup
            soup = BeautifulSoup(html_content, 'html.parser')

            job_listings = soup.find_all('h2', {'class': 'jobTitle'})
            base_job_url='https://www.indeed.com/viewjob?jk='
            # Process job listings on the current page
            for job in job_listings:
                if len(scraped_data) == job_number:
                    print('reached max jobs needed!')
                    break


                try:
                    anchor_tag = job.find('a', class_='jcs-JobTitle')
                    job_key = anchor_tag['data-jk']
                    job_url = f"{base_job_url}{job_key}"
                    print(job_url)
                    for retry_count in range(max_retries):
                        try:
                            await page.goto(job_url, timeout=120000)
                            await page.wait_for_load_state('load')

                            if await page.query_selector('.jobsearch-JobComponent'):
                                try:
                                    index += 1
                                    print(f'Successfully reached job number {index} listing site')

                                    html_content = await page.evaluate('()=>document.documentElement.outerHTML')
                                    soup = BeautifulSoup(html_content, 'html.parser')
                                    title = soup.find('h1', {'class': 'jobsearch-JobInfoHeader-title'}).find('span').text.strip()
                                    print(title)
                                    company_name =None
                                    company_url =None

                                    company_data = soup.find('div', {'class': 'jobsearch-CompanyInfoWithoutHeaderImage'}) #.find('span',{'class':'css-1cxc9zk'}).find('a', class_='css-1l2hyrd')
                                    if company_data:
                                        company_name = company_data.text.strip()
                                        company_data_2=company_data.find('a', class_='css-1l2hyrd')
                                        if company_data_2:
                                            company_url = company_data['href']
                                        print(company_name)



                                    location_div = soup.find('div',{'id': 'jobLocationText'})
                                    if location_div:
                                        # Find any nested element under the location_div
                                        nested_element = location_div.find()

                                        # Extract text from the nested element
                                        if nested_element:
                                            nest_nest_element = nested_element.find()
                                            if(nest_nest_element):
                                                location = nest_nest_element.text.strip()
                                            else:
                                                location = nested_element.text.strip()
                                        else:
                                            print("No nested element found under 'jobLocationText' div")
                                            location = None
                                    else:
                                        print("Location div not found")
                                        location=None

                                    print(location)


                                    about_div = soup.find('div',{'id': 'jobDescriptionText'})
                                    about=''
                                    if about_div:
                                        about = about_div.get_text(separator=' ').strip()



                                    scraped_data.append(
                                        {'Title': title, 'Company_Name': company_name, 'Company_URL': company_url,
                                         'Job_Location': location, 'Seniority_level': None,
                                         'Employment_type': None, 'Job_function': None,
                                         'Industries': None, 'About': about,'Job_URL':job_url,'Posted':None,'Collected':current_date_and_time})
                                    print(f"Title: {title}\nCompany: {company_name}\n")
                                    break
                                except Exception as e:
                                    print(f"exception when job scraping!! {e}")
                                    break
                            else:
                                print(f'Not reached job numer {index} site')
                                break
                        except Error as e:
                            print(f"Error when goto occurred: {e}")
                            if retry_count == 50 or retry_count == 70:
                                print("Trying to open new browser in job listing block")
                                browser = await pw.chromium.connect_over_cdp(browser_url)
                                print("connected to new browser")
                                page = await browser.new_page()
                                print('open new page')
                except Error as e:
                    print(f"Error occurred: {e}")
                    # Handle the error here if needed

        await browser.close()
        write_to_file(scraped_data=scraped_data)

async def zip_scraping(keyword,j_location,job_number):
    """
        Asynchronously scrapes job listings from ZipRecruiter based on the provided keyword.

        Args:
        - keyword (str): The search keyword for job listings.
        - job_number (int): The maximum number of job listings to scrape.

        Returns:
        - None

        Utilizes Playwright to scrape job listings from ZipRecruiter, extracting details such as title, company name, location, etc.
        Saves the scraped data to a CSV file.

        Note:
        - This function requires Playwright library and Python 3.7+ for asynchronous operations.
        - Ensure 'browser_url' is defined before invoking this function.
        """
    def write_to_file(scraped_data):
        """
                            Writes scraped job data to 'zip_jobs.csv' in CSV format.

                            Args:
                            - scraped_data (list of dicts): List of dictionaries containing job data.

                            Returns:
                            - None

                            Writes 'scraped_data' to a CSV file with specific fieldnames:
                            'Title', 'Company_Name', 'Company_URL', 'Job_Location', 'Seniority_level',
                            'Employment_type', 'Job_function', 'Industries', 'About', 'Job_URL',
                            'Posted', and 'Collected'. Prints a message upon successful completion.

                            Example:
                            >>> write_to_file(scraped_data)
                            """
        csv_file = 'zip_jobs.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['Title', 'Company_Name', 'Company_URL', 'Job_Location',
                                                      'Seniority_level', 'Employment_type', 'Job_function',
                                                      'Industries', 'About','Job_URL','Posted','Collected'])
            writer.writeheader()
            writer.writerows(scraped_data)

            print(f"Scraped data saved to '{csv_file}'.")


    async with async_playwright() as pw:
        max_retries = 50
        print('connect')
        browser = await pw.chromium.connect_over_cdp(browser_url)
        print("connected")
        page = await browser.new_page()  # Open new page

        # Define the base URL for the job search
        base_url = f"https://www.ziprecruiter.com/jobs-search?location={j_location}&keywords={keyword}&page="

        # Define search parameters


        max_pages = 200  # Maximum number of pages to scrape
        scraped_data = []
        index = 0
        page_number=0
        for page_num in range(max_pages):
            if len(scraped_data) == job_number:
                print('reached max jobs needed!')
                break  # Stop scraping if 5000 jobs have been scraped

            # Update the start parameter for each page
            page_number+=1

            url = f"{base_url}{page_number}"
            print(url)

            # Retry navigating to the page for a certain number of times
            for retry_count in range(max_retries):
                try:
                    await page.goto(url, timeout=120000)  # Go to LinkedIn job search page
                    await page.wait_for_load_state('load')
                    # html = await page.content()
                    # with open("output.txt", "w", encoding="utf-8") as file:
                    #     # Write your string/content to the file
                    #     file.write(html)
                    # return
                    # Check if the page contains job listings
                    if await page.query_selector('#react-job-results-root'):
                        print(f"Successfully reached search results page for page {page_num}.")
                        break  # Break out of the loop if successful
                    else:
                        print(f"Not on search results page for page {page_num}. Retrying...")
                        print("Trying to open new browser")
                        browser = await pw.chromium.connect_over_cdp(browser_url)
                        print("connected to new browser")
                        page = await browser.new_page()
                        print('open new page')
                except Error as pe:
                    print(f"Error occurred: {pe}")
                    if retry_count == 50 or retry_count > 60:
                        print("Trying to open new browser")
                        browser = await pw.chromium.connect_over_cdp(browser_url)
                        print("connected to new browser")
                        page = await browser.new_page()
                        print('open new page')
                    elif retry_count < max_retries - 1:
                        print(f"Retrying... Attempt {retry_count + 1}")


                    else:
                        print("Max retries exceeded. Exiting.")
                        await browser.close()
                        write_to_file(scraped_data=scraped_data)
                        return

            # Extract href attributes using Playwright
            html_content = await page.evaluate('()=>document.documentElement.outerHTML')

            # Parse the HTML with Beautiful Soup
            soup = BeautifulSoup(html_content, 'html.parser')

            job_listings = soup.find_all('article', {'class': 'group'})

            # Process job listings on the current page
            for job in job_listings:
                if len(scraped_data) == job_number:
                    print('reached max jobs needed!')
                    break # Stop scraping if 5000 jobs have been scraped


                try:
                    for retry_count in range(max_retries):
                        try:

                                try:
                                    index += 1
                                    print(f'Successfully reached job number {index} listing site')
                                    title = job.find('a',{'class':'break-words'}).text.strip()
                                    job_url = job.find('a',{'class':'break-words'})['href']
                                    print(title)
                                    print(job_url)
                                    company_name = job.find('a', {'data-testid': 'job-card-company'}).text.strip()
                                    company_url = job.find('a', {'data-testid': 'job-card-company'})['href']
                                    print(company_name)
                                    print(company_url)
                                    location = job.find('a', {'data-testid': 'job-card-location'}).text.strip()
                                    print(location)
                                    p = job.find('div', {'class': 'flex flex-col'}).find_all('p', {'class': 'text-black normal-case text-body-md'})
                                    if len(p) == 1:
                                        type = p.text.strip()
                                    else:
                                        type = p[1].text.strip()
                                    print(type)







                                    scraped_data.append(
                                        {'Title': title, 'Company_Name': company_name, 'Company_URL': company_url,
                                         'Job_Location': location, 'Seniority_level': None,
                                         'Employment_type': type, 'Job_function': None,
                                         'Industries': None, 'About': None,'Job_URL':job_url,'Posted':None,'Collected':current_date_and_time})
                                    print(f"Title: {title}\nCompany: {company_name}\n")
                                    break
                                except Exception as e:
                                    print(f"exception when job scraping!! {e}")
                                    break

                        except Error as e:
                            print(f"Error when goto occurred: {e}")
                            if retry_count == 50 or retry_count == 70:
                                print("Trying to open new browser in job listing block")
                                browser = await pw.chromium.connect_over_cdp(browser_url)
                                print("connected to new browser")
                                page = await browser.new_page()
                                print('open new page')
                except Error as e:
                    print(f"Error occurred: {e}")
                    # Handle the error here if needed

        await browser.close()
        write_to_file(scraped_data=scraped_data)

async def profile_scrape(url,user_details):
    import csv

    def write_to_file(scraped_data):
        csv_file = 'profile_data.csv'
        fieldnames = ['about', 'avatar', 'certifications', 'city', 'country_code', 'current_company',
                      'current_company:company_id',
                      'current_company:name', 'education', 'educations_details', 'experience', 'followers', 'following',
                      'groups', 'id', 'languages', 'name', 'people_also_viewed', 'position', 'posts', 'recommendations',
                      'recommendations_count', 'timestamp', 'url', 'volunteer_experience', 'сourses']

        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(scraped_data)

        print(f"Scraped data saved to '{csv_file}'.")

    async with async_playwright() as pw:
        max_retries = 50
        print('connect')
        browser = await pw.chromium.connect_over_cdp(browser_url)
        print("connected")
        page = await browser.new_page()  # Open new page
        scraped_data = []



        # Retry navigating to the page for a certain number of times
        for retry_count in range(max_retries):
            try:
                await page.goto(url, timeout=120000)
                await page.wait_for_load_state('load')

                if await page.query_selector('.profile'):
                    print(f"Successfully reached search results page for profile page.")
                    break  # Break out of the loop if successful
                else:
                    print(f"Not on search results page for profile page. Retrying...")
                    print("Trying to open new browser")
                    browser = await pw.chromium.connect_over_cdp(browser_url)
                    print("connected to new browser")
                    page = await browser.new_page()
                    print('open new page')
            except Error as pe:
                print(f"Error occurred: {pe}")
                if retry_count == 50 or retry_count == 70:
                    print("Trying to open new browser")
                    browser = await pw.chromium.connect_over_cdp(browser_url)
                    print("connected to new browser")
                    page = await browser.new_page()
                    print('open new page')
                elif retry_count < max_retries - 1:
                    print(f"Retrying... Attempt {retry_count + 1}")


                else:
                    print("Max retries exceeded. Exiting.")
                    await browser.close()
                    write_to_file(scraped_data=scraped_data)
                    return

        # Extract href attributes using Playwright
        html_content = await page.evaluate('()=>document.documentElement.outerHTML')

        # Parse the HTML with Beautiful Soup
        soup = BeautifulSoup(html_content, 'html.parser')

        profile = soup.find('section', {'class': 'profile'})
        try:
            name = profile.find('h1', {'class': 'top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0'}).text.strip()
            print(name)
        except Exception as e:
            print(f"exception when job scraping!! {e}")
        info = []
        try:
            divs = soup.find_all('div', {'class': 'not-first-middot'})
            for div in divs:
                spans = div.find_all('span')
                for span in spans:
                    info.append(span.text.strip())
        except Exception as e:
            print(f"exception when job scraping!! {e}")
        location = None
        if len(info) >0:
            location = info[0]
        followers = None
        if len(info) > 2:
            followers = info[2]
        connections = None
        if len(info) > 3:
            connections = info[3]
        c_position = soup.find('div', {'data-section': 'currentPositionsDetails'})
        if c_position:
            c_company = c_position.find('span', {'class': 'top-card-link__description line-clamp-2'})
            if c_company:
                c_company=c_company.text.strip()
        else:
            c_position = None
        education = soup.find('div', {'data-section': 'educationsDetails'})
        if education:
            c_education = education.find('span', {'class': 'top-card-link__description line-clamp-2'})
            if c_education:
                c_education=c_education.text.strip()
        else:
            c_education = None

        scraped_data.append(
            {'about': user_details['About'],'avatar':None,'certifications':user_details['Certifications'],'city':location,'country_code':user_details['Country Code'],
             'current_company':user_details['Current Company'],'current_company:company_id':None,'current_company:name':c_company,'education':user_details['Education'],'educations_details':c_education,
             'experience':user_details['Experience'],'followers':followers,'following':connections,'groups':None,'id':None,'languages':user_details['Languages'],'name':name,'people_also_viewed':None,
             'position':user_details['Position'],'posts':None,'recommendations':None,'recommendations_count':None,'timestamp':None,'url':url,'volunteer_experience':None,'сourses':user_details['Courses']})









        await browser.close()
        write_to_file(scraped_data=scraped_data)


def combine_jobs():
    # Get a list of all CSV files in the directory
    csv_files = glob.glob('*.csv')

    # List to hold all dataframes
    dfs = []

    # Read each CSV file and append to the list
    for file in csv_files:
        df = pd.read_csv(file)
        dfs.append(df)

    # Concatenate all dataframes into a single dataframe
    combined_df = pd.concat(dfs)

    # Remove duplicate rows
    combined_df = combined_df.drop_duplicates()

    # Write the result to a new CSV file
    combined_df.to_csv('all_jobs.csv', index=False)

    print("Combined CSV files and removed duplicates successfully!")
if __name__ == '__main__':

    app = UserDetailsForm()
    app.mainloop()
    user_details = app.get_user_details()
    profile_url=user_details['Work Preference']['Profile_URL']
    keywords=user_details['Work Preference']['Keywords']
    location = user_details['Work Preference']['Location']
    job_type = user_details['Work Preference']['Job Type']
    print('start')
    asyncio.run(profile_scrape(profile_url,user_details=user_details))
    asyncio.run(linkedin_scraping(keywords,location,link_jobs_num))
    asyncio.run(indeed_scraping(keywords, location, indeed_jobs_num))
    asyncio.run(zip_scraping(keywords, location, zip_jobs_num))


