import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, MoveTargetOutOfBoundsException

import pandas as pd
import numpy as np


def get_description(product_link):
    ##click on first item
    browser.get(product_link)

    ##wait/load collapsable title
    ##timeout at 50 server ticks
    timeout=50
    try:
        WebDriverWait(browser,timeout).until(EC.visibility_of_element_located((By.CLASS_NAME,
                     'collapsable__title')))
    except TimeoutException:
        browser.quit()
        
    ##identify collapsable element
    collapsable_element = browser.find_element_by_class_name('collapsable__title')
    
    #scroll into view
    browser.execute_script("arguments[0].scrollIntoView(true);", collapsable_element)
    
    ##click on collapsable element
    webdriver.ActionChains(browser).move_to_element(collapsable_element).click(collapsable_element).perform()
    
    ##find description
    description = browser.find_element_by_class_name('collapsable__content').text
    
    #repeat action until description found
    while description == '':
        
        try:
            #scroll into view
            browser.execute_script("arguments[0].scrollIntoView(false);", collapsable_element)
        
            ##click on collapsable element
            webdriver.ActionChains(browser).move_to_element(collapsable_element).click(collapsable_element).perform()
        except MoveTargetOutOfBoundsException:
            #scroll into view
            browser.execute_script("arguments[0].scrollIntoView(false);", collapsable_element)
    
        ##find description
        description = browser.find_element_by_class_name('collapsable__content').text
    
    #return description
    return(description)


#set scraping browser
browser = webdriver.Firefox()
browser.get('https://mejuri.com/shop/t/type')

#wait/load all products
#timeout at 50 server ticks
timeout=50
try:
    WebDriverWait(browser,timeout).until(EC.visibility_of_all_elements_located((By.CLASS_NAME,
                 'category-product')))
except TimeoutException:
        browser.quit()

#lazyloading
# Get scroll height
last_height = browser.execute_script("return document.body.scrollHeight")
while True:
    # Scroll down to bottom
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # wait to load page
    time.sleep(30)
    # Calculate new scroll height and compare with last scroll height
    new_height = browser.execute_script("return document.body.scrollHeight")
    if new_height == last_height: # which means end of page
        break
    # update the last height
    last_height = new_height
    
    
#collect all collection elements  
collection_containers = browser.find_elements_by_class_name('collections-products__collection')

#create lists to store elements
product_containers = []
collection_names = []

product_id = []
product_link = []
material = []

product_images = []
product_metrics = []

price_CAD = []

mainimg_src = []
altimg_src = []

product_name = []

#cycle through collection elements,
for collection in collection_containers:
    #sequentially store all products per collection
    product_containers.append(collection.find_elements_by_class_name('category-product'))
    #store all collection names
    collection_names.append(collection.find_element_by_css_selector('div[class="collection-title"]').text)

#cycle through collections,
for products in product_containers:
    #cycle through products in each collection
    for product in products:
        #find product ids, product names, and product materials
        product_id.append(product.find_element_by_class_name('category-product__container').get_attribute('id'))
        product_link.append(product.find_element_by_class_name('category-product__image-link').get_attribute('href'))
        material.append(product.get_attribute('data-material'))
        
        #find all product image tags
        product_images.append(product.find_elements_by_tag_name('img'))
        #find all product metrics
        product_metrics.append(product.find_element_by_class_name('category-product__metrics'))
        
        #find product prices
        price_CAD.append(product.find_element_by_css_selector('p[class="product-price product-price--CAD small"]').text)

#cycle through product images,        
for image in product_images:
    #find main image
    mainimg_src.append(image[0].get_attribute('src'))
    #find alt image
    altimg_src.append(image[1].get_attribute('src'))
    
#cycle through product metrics,
for metric in product_metrics:
    #find product names
    product_name.append(metric.find_element_by_tag_name('a').text)


product_collections = []
#cycle through products in collections,
for collection, products in enumerate(product_containers):
    #create list of collection name over the number of products in collection 
    product_collections.append([collection_names[collection]]*len(products))
#unpack multidimensional list
product_collections = [product for collections in product_collections for product in collections]


#get index of unique product names
unique_product_names, indexes = np.unique(product_name, return_index=True)
#initialize empty dictionary
product_description = {}
#cycle through unique product names and indexes,
for product, index in zip(unique_product_names,indexes):
    #update dictionary with unique product name & description
    product_description.update({product:get_description(product_link[index])})
    
    
#create dictionary to store all product variables
data = {'product_id':product_id, 'price_CAD':price_CAD, 
        'product_name':product_name, 'product_link':product_link, 
        'collection':product_collections, 'material':material, 
        'main_img':mainimg_src, 'alt_img':altimg_src}

#create pandas dataframe from product variables
products = pd.DataFrame.from_dict(data)

#convert price to numeric
products['price_CAD'] = pd.to_numeric(products.price_CAD)

#add description based on product name
products['description'] = products.product_name.map(product_description)

#ensure
products = products[['product_id','price_CAD','product_name','product_link','collection','material','main_img','alt_img']]

#output to csv
products.to_csv('mejuri_products_data.csv',index=False)