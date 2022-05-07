#!/usr/bin/env python
# coding: utf-8



from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
import requests
from getpass import getpass
from parsel import Selector





def LinkedIn_login():
    
       
    username = input("Insert your LinkedIn email account: ")
    pword = getpass("Insert your Linkedin password: ")
    
    driver = webdriver.Chrome("chromedriver")
    
    driver.get("https://linkedin.com/uas/login")
    
    # entering username
    username_tag = driver.find_element_by_id("username")
    
    # Enter Your Email Address
    username_tag.send_keys(username)  
    
    # entering password
    pword_tag = driver.find_element_by_id("password")
    
    # In case of an error, try changing the element 
    # tag used here.

    # Enter Your Password
    pword_tag.send_keys(pword)        

    # click
    driver.find_element_by_xpath("//button[@type='submit']").click()
    
    return driver



class profile_scrape (object):
    
    """
    Description - xxx
    """
    
    def __init__(self, profile_id, driver):
        
        # LinkedIn user ID
        self.profile_id = profile_id

        # Selenium driver to use
        self.driver = driver

        
    def get_profile(self):
        
        """
        input: "profile_id" - the LinkedIn profle to scrape, e.g., "john-doe-1234".
        """
                
        # URL generation for access        
        profile_url = f"https://www.linkedin.com/in/{self.profile_id}/"
        
        # Move on Chrome to the LinkedIn page above
        self.driver.get(profile_url)
        
        # Time sleep for page rendering
        time.sleep(5)
        
        # Getting HTML script
        self.src_html = self.driver.page_source
        
        # Parsing the HTML using BS4
        self.soup  = BeautifulSoup(self.src_html, 'html.parser') # 'lxml', "html.parser"
        
        
        
    
    def scroll_down(self):
        
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        # will be used in the while loop
        initialScroll = 0
        finalScroll = 1000
        
        while True:
            self.driver.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
            # this command scrolls the window starting from
            # the pixel value stored in the initialScroll 
            # variable to the pixel value stored at the
            # finalScroll variable
            initialScroll = finalScroll
            finalScroll += 1000

            # we will stop the script for 3 seconds so that 
            # the data can load
            time.sleep(1)
            # You can change it as per your needs and internet speed
            if finalScroll > last_height:
                break
    
    
    
    
    def button_exist(self):

        """
        This method is to check if there are buttons of "show more" in each item, 
        including "experience", "skills", or "education"
        """
        
        buttons = self.soup.find_all("span", {'class': 'pvs-navigation__text'})
        
        self.exp_ind, self.skl_ind, self.educ_ind = 999, 999, 999
        
        for ind,button in enumerate(buttons):
            if ("experiences" in button.text) & ("volunteer" not in button.text):
                self.exp_ind = ind

            elif "skills" in button.text:
                self.skl_ind = ind

            elif "education" in button.text:
                self.educ_ind = ind
        
        if self.exp_ind == 999:
            self.exp_indicator = False
            print("This profile has no expanded experiences.")
            
        else:
            self.exp_indicator = True
            print(f"This profile has `Show more experiences' in item No.{self.exp_ind}.")
            
    def education(self):

        self.education_output = []

        main_items = self.soup.find_all("div", {"class":"pvs-header__container"})

        self.education_ind = -1

        for item in main_items:
            
            temp_item = item.find("span", {"class":"visually-hidden"}).text

            if ("About" not in temp_item) & ("Featured" not in temp_item):
                self.education_ind +=1 
            
            if "Education" in temp_item: #"About", "Featured"
                break


        self.education = self.soup.find_all("ul", {"class":"pvs-list ph5 display-flex flex-row flex-wrap"})[self.education_ind]
        self.education_items = self.education.find_all("div", {"class":"pvs-entity pvs-entity--padded pvs-list__item--no-padding-when-nested"})

        for temp_degree in self.education_items:

            college_ind, degree_ind, period_ind = 0, 1, 2 

            # college
            try:
                college = temp_degree.find_all("span", {"class":"visually-hidden"})[college_ind].text
            except:
                college = "NA"

            # degree
            try:
                degree = temp_degree.find_all("span", {"class":"visually-hidden"})[degree_ind].text
            except:
                degree = "NA"
            
            # period
            try:
                period = temp_degree.find_all("span", {"class":"visually-hidden"})[period_ind].text

            except:
                period = "NA"

            self.education_output.append( (self.profile_id, college, degree, period ))

        time.sleep(3)

    def experience_locator(self):
        
        if self.exp_ind == 999: # i.e., if there is no "show more experiences" button
            
            self.items = self.soup.find_all("ul", {"class":"pvs-list ph5 display-flex flex-row flex-wrap"})
            self.case_1_exp_ind = 0
            for ind, item in enumerate(self.items):
    
                temp_item = item.find_all("a", {"data-field":"experience_company_logo"})
    
                if len(temp_item) >0: 
                    self.case_1_exp_ind = ind
                    #print(f"The index of ``Experienc'' is {ind}")
                    
            # Experience records        
            self.exps = self.soup.find_all("ul", {"class":"pvs-list ph5 display-flex flex-row flex-wrap"})[self.case_1_exp_ind]

            # bullet point counts
            self.len_bullet = len(self.exps.find_all("span", {"class":"mr1 hoverable-link-text t-bold"}))

            self.exp_items = self.exps.find_all("div",{"class":"pvs-entity pvs-entity--padded pvs-list__item--no-padding-when-nested"})

        else: # i.e., if there is "show more experience tab"

            page_exp = self.driver.find_elements_by_xpath("//span[@class = 'pvs-navigation__text']")[self.exp_ind]

            # Y_coord of "show all experiences" button
            exp_y_cood = self.driver.find_elements_by_xpath("//span[@class = 'pvs-navigation__text']")[self.exp_ind].location["y"]

            self.driver.execute_script(f"window.scrollTo({exp_y_cood-1000},{exp_y_cood-500})")
            
            # click
            page_exp.click()
            
            # time sleep
            time.sleep(5)
            
            # Parsing the clicked page
            self.expanded_html = self.driver.page_source
            self.soup = BeautifulSoup(self.expanded_html, 'html.parser')


            # bullet point counts
            self.len_bullet = len(self.soup.find_all("span", {"class":"mr1 hoverable-link-text t-bold"}))

            self.exp_items = self.soup.find_all("div",{"class":"pvs-entity pvs-entity--padded pvs-list__item--no-padding-when-nested"})


    
    def info_scraper(self):
        
        self.output_list = []
        
        if self.len_bullet == 0: 
        
            for item in self.exp_items:

                company = item.find_all("span", {"class":"t-14 t-normal"})[0].find("span", {"class":"visually-hidden"}).text

                position = item.find_all("span", {"class":"mr1 t-bold"})[0].find("span", {"class":"visually-hidden"}).text

                period_ind = 0
                period_tenure = item.find_all("span", {"class":"t-14 t-normal t-black--light"})[period_ind].find("span", {"class":"visually-hidden"}).text

                # period
                period = period_tenure.split(" · ")[0] # `0` - period

                # tenure
                tenure = period_tenure.split(" · ")[1] # `1` - tenure

                # start year 
                start_year = re.findall(r'\d+', period)[0]  # `0` - start year

                # end year
                try:
                    end_year = re.findall(r'\d+', period)[1] # `1` - end year
                except:
                    end_year = "Present"

                
                # area
                area_ind = 1
                try:
                    area = item.find_all("span", {"class":"t-14 t-normal t-black--light"})[area_ind].find("span", {"class":"visually-hidden"}).text
                except: area = "NA"

                # description
                try:
                    description = item.find_all("div", {"class":"pv-shared-text-with-see-more t-14 t-normal t-black display-flex align-items-center"})[0].find("span", {"class":"visually-hidden"}).text 
                except:
                    description = "NA"


                #print(company, position, start_year, end_year, tenure, area, description)
               
                self.output_list.append((company, position, start_year, end_year, tenure, area, description ))
            

        else: # i.e., if there are multiple positions in a company (= bullet points exist)

             for item in self.exp_items:

                # Check if the current item has bullet point
                bullet_cnt = len(item.find_all("span", {"class":"mr1 hoverable-link-text t-bold"}))

                if bullet_cnt > 0: # i.e., if the item has bullet points

                    company_position = item.find_all("span", {"class":"mr1 hoverable-link-text t-bold"})

                    # period and tenure
                    self.period_tenure = item.find_all("span", {"class":"t-14 t-normal t-black--light"})
                    self.period_tenure = [ temp_item.find("span", {"class":"visually-hidden"}).text for temp_item in self.period_tenure]

                    # remove non-period string
                    for temp_item in self.period_tenure[1:]: #<------- the starting index should be "1" in order to keep the "area" (e.g., `Houston, TX'), which will be used through iterations.
                        if len(re.findall(r'\d+', temp_item)) ==0:
                            self.period_tenure.remove(temp_item)

                    # add `NA' to fix the length
                    if len(re.findall(r'\d+', self.period_tenure[0])) > 0:
                        self.period_tenure.insert(0, "NA")


                    # company and area
                    company = company_position[0].find("span", {"class":"visually-hidden"}).text
                    area = self.period_tenure[0]

                    # description
                    desc_tag = item.find_all("div", {"class":"pv-shared-text-with-see-more t-14 t-normal t-black display-flex align-items-center"})
                    desc_tag_text = [tag.find("span", {"class":"visually-hidden"}).text for tag in desc_tag]
                    desc_text= "\n".join(desc_tag_text)

                    if len(desc_tag) == 0:
                        
                        desc_tag = item.find_all("div", {"class":"display-flex align-items-center t-14 t-normal t-black"})
                        desc_tag_text = [tag.find("span", {"class":"visually-hidden"}).text for tag in desc_tag]
                        desc_text= "\n".join(desc_tag_text)



                    for ind in range(1, len(company_position)): #<--------- the range starts from index "1" 
                        position = company_position[ind].find("span", {"class":"visually-hidden"}).text
                        period_tenure_temp = self.period_tenure[ind]

                        period_temp = period_tenure_temp.split(" · ")[0]
                        tenure = period_tenure_temp.split(" · ")[1]
                        start_year = re.findall(r'\d+', period_temp)[0]

                        try:
                            end_year = re.findall(r'\d+', period_temp)[1]
                        except:
                            end_year = "Present"

                        if ind == 1:
                            description = desc_text
                        else:
                            description = ""

                        
                        self.output_list.append( (company, position, start_year, end_year, tenure, area, description) )

                else:
                    company = item.find_all("span", {"class":"t-14 t-normal"})[0].find("span", {"class":"visually-hidden"}).text

                    position = item.find_all("span", {"class":"mr1 t-bold"})[0].find("span", {"class":"visually-hidden"}).text

                    period_ind = 0
                    period_tenure = item.find_all("span", {"class":"t-14 t-normal t-black--light"})[period_ind].find("span", {"class":"visually-hidden"}).text

                    # period
                    period = period_tenure.split(" · ")[0] # `0` - period

                    # tenure
                    tenure = period_tenure.split(" · ")[1] # `1` - tenure

                    # start year 
                    start_year = re.findall(r'\d+', period)[0]  # `0` - start year

                    # end year
                    try:
                        end_year = re.findall(r'\d+', period)[1] # `1` - end year
                    except:
                        end_year = "Present"

                    
                    # area
                    area_ind = 1
                    try:
                        area = item.find_all("span", {"class":"t-14 t-normal t-black--light"})[area_ind].find("span", {"class":"visually-hidden"}).text
                    except: area = "NA"

                    # description
                    try:
                        desc_tag = item.find_all("div", {"class":"pv-shared-text-with-see-more t-14 t-normal t-black display-flex align-items-center"})
                        desc_tag_text = [tag.find("span", {"class":"visually-hidden"}).text for tag in desc_tag]
                        description= "\n".join(desc_tag_text)
                    except:
                        description = "NA"

                    # This if-statement is for the cases like ``hahaha1220'' with `show more experiences` button
                    if len(desc_tag) == 0:
                        try:
                            desc_tag = item.find_all("div", {"class":"display-flex align-items-center t-14 t-normal t-black"})
                            desc_tag_text = [tag.find("span", {"class":"visually-hidden"}).text for tag in desc_tag]
                            description= "\n".join(desc_tag_text)
                        except:
                            description = "NA"


                    #print(company, position, start_year, end_year, tenure, area, description)
                
                    self.output_list.append((company, position, start_year, end_year, tenure, area, description ))



if __name__ == "__main__":
    print("xxx")
    
    
    

        


        
    


