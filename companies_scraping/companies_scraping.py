import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd


username='brd-customer-hl_80709a30-zone-dc_shalev'
password='babah28udbeg'
auth= f'{username}:{password}'
host = 'brd.superproxy.io:9222'
browser_url = f'wss://{auth}@{host}'
all_jobs = pd.read_csv(r"C:\Users\shale\Downloads\more_jobs.csv")
companies_url = list(all_jobs['url_final'].unique())
results_dict = {}
len_df = len(companies_url)

async def main():


    async with async_playwright() as pw:

        print('connecting')
        browser = await pw.chromium.connect_over_cdp(browser_url)
        print('connected')
        page = await browser.new_page()
        print('goto')
        counter = 1918
        counter_save = 1918
        for url in companies_url[1918:]:
            try:
                company_url =  url
                await page.goto(company_url, timeout=120000)


                # Get the entire HTML content
                html_content = await page.evaluate('()=>document.documentElement.outerHTML')

                # Parse the HTML with Beautiful Soup
                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract the 'About us' description
                description_element = soup.select_one('.core-section-container[data-test-id="about-us"] p[data-test-id="about-us__description"]')
                description = description_element.text if description_element else None
                # print('Description:')
                # print(description)

                # Extract the 'Company size'
                company_size_element = soup.select_one('div[data-test-id="about-us__size"] dd')
                company_size = company_size_element.text.strip() if company_size_element else None
                # print('Company size:')

                company_industry_element = soup.select_one('div[data-test-id="about-us__industry"] dd')
                company_industry = company_industry_element.text.strip() if company_industry_element else None


                results_dict[company_url] = (description, company_size, company_industry)
                data = [(key, *value) for key, value in results_dict.items()]

                # Convert the list of tuples to a DataFrame
                df = pd.DataFrame(data, columns=['URL', 'Description', 'Company Size', 'Industry'])
                df.to_csv(f'companies_scraped_from{counter_save}.csv')
                print(counter)
                counter += 1
            except:
                print(f"Failed in company: {counter}")
                counter += 1


        await browser.close()

    data = [(key, *value) for key, value in results_dict.items()]

    # Convert the list of tuples to a DataFrame
    df = pd.DataFrame(data, columns=['URL', 'Description', 'Company Size','Industry'])
    df.to_csv('companies_scraped.csv')
# Run the async function
asyncio.run(main())