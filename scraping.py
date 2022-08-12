# Import Splinter and BeautifulSoup
from distutils.command.install_egg_info import safe_name
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt
import requests

def scrape_all():
    #Initiate headless driver for deployment 
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

   # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemispheres(browser)
        }  

    # Stop webdriver and return data
    browser.quit()
    return data 

def mars_news(browser):

    # Scrape Mars News 

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'

    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')

    #Add try/except for error handling
    
    try:

        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'      
        news_title = slide_elem.find('div',class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
       
    except AttributeError:
        return None, None

    return news_title, news_p

# ## JPL Space Images Featured Image

def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    #Add try/except for error handling

    try:
    
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None   

    # Use the base URL to create an absolute URL
    img_url= f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

# ## Mars Facts 
 
def mars_facts():

    #Add try/except for error handling
    try:

        # Use 'read_html' to scrape thdf = pd.e facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None


    #Assign columns and set index of dataframe 
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap

    return df.to_html(classes="table table-striped")

def hemispheres(browser):
    url='https://marshemispheres.com/'

    browser.visit(url + 'index.html')

     # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    
    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    # Scrape the top ten tags
    links = browser.find_by_css('a.product-item img')
    for i in range(4):
        browser.find_by_css('a.product-item img')[i].click()
        hemi_data = scrape_hemisphere(browser.html)
        hemi_data['img_url'] = url + hemi_data['img_url']
        hemisphere_image_urls.append(hemi_data) 
        browser.back()
    return hemisphere_image_urls 

def scrape_hemisphere(html_text):
    #parse html text
    hemi_soup = soup(html_text, 'html.parser')
    hemisphere_image_urls = []
    #Adding try/except for error handling
    try:
        #hemispheres['title']=Browser.find_by_css('h2.title').get_text()
        #hemisphere_image_urls.append(hemispheres)
        #.find('div',class_='content_title').get_text()
        title_elem = hemi_soup.find('h2',class_='title').get_text()
        sample_elem = hemi_soup.find('img',class_='thumb').get('src')
    except AttributeError: 

         # Image error will return None
        title_elem = None
        sample_elem = None

    hemispheres = {"title":title_elem,
               "img_url":sample_elem
                }
        #print(hemispheres)
    return hemispheres

if __name__ == "__main__":

        # If running as script, print scraped data
        print(scrape_all())

