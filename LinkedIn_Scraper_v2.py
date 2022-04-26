#!/usr/bin/env python
# coding: utf-8

# In[5]:


from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
import requests



# In[73]:


def LinkedIn_login():
    
    username = "ssirasoni13@gmail.com"
    pword = "1730_Libertylane"
    
    #self.username = input("Insert your LinkedIn email account: ")
    #self.pword = input("Insert your Linkedin password: ")
    
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

    
  






class profile_scrape (object):
    
    """
    Description
    """
    
    def __init__(self, profile_id, driver):
        
        self.profile_id = profile_id
        self.driver = driver
        self.driver.set_window_size(1024, 768)

        
    
    def get_profile(self):
        
        """
        input: "profile_id" - the LinkedIn profle to scrape, e.g., "john-doe-1234".
        """
                
        profile_url = f"https://www.linkedin.com/in/{self.profile_id}/"
        
        self.driver.get(profile_url)
        
        time.sleep(10)
        
        self.src_html = self.driver.page_source
        
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
        
        buttons = self.soup.find_all("span", {'class': 'pvs-navigation__text'})
        
        self.exp_ind, self.skl_ind = 999, 999
        
        for ind,button in enumerate(buttons):
            if ("experiences" in button.text) & ("volunteer" not in button.text):
                self.exp_ind = ind

            elif "skills" in button.text:
                self.skl_ind = ind
        
        if self.exp_ind == 999:
            self.exp_indicator = False
            print("This profile has no expanded experiences.")
            
        else:
            self.exp_indicator = True
            print(f"This profile has to `Show more experiences' in item No.{self.exp_ind}.")
            
   

    ################################################
    ### Case 1 - WITHOUT "Show more experiences" ###
    ################################################
    
    
    def case_1_exp_locator(self):
        
        if self.exp_ind == 999:
            
            self.items = self.soup.find_all("ul", {"class":"pvs-list ph5 display-flex flex-row flex-wrap"})
            self.case_1_exp_ind = 0
            for ind, item in enumerate(self.items):
    
                temp_item = item.find_all("a", {"data-field":"experience_company_logo"})
    
                if len(temp_item) >0: 
                    self.case_1_exp_ind = ind
                    print(f"The index of Experience is {ind}")
                    
                    
            self.exps = self.soup.find_all("ul", {"class":"pvs-list ph5 display-flex flex-row flex-wrap"})[self.case_1_exp_ind]

            self.exps_bullet = self.exps.find_all("span", {"class":"mr1 hoverable-link-text t-bold"})
            self.len_bullet = len(self.exps_bullet)

            self.exp_items = self.exps.find_all("div",{"class":"pvs-entity pvs-entity--padded pvs-list__item--no-padding-when-nested"})
    
    
    def case_1_scraper(self):
        
        
        
        self.output_list = []
        
        if self.len_bullet == 0:
            
            ######################################################
            ### Case 1.1 - No "show more" & No "bullet points" ###
            ######################################################
            
           # companies
            companies = self.exps.find_all("span", {"class":"t-14 t-normal"})
            
            # positions
            positions = self.exps.find_all("span", {"class":"mr1 t-bold"})
            
            # periods
            periods = self.exps.find_all("span", {"class":"t-14 t-normal t-black--light"})
            
            start_years =[]
            end_years =[]
            
            for temp_period in periods:
                
                period = temp_period.find_all("span", {"class":"visually-hidden"})[0].text.split(" · ")[0]
                
                reg_ex = re.findall(r'\d+', period)
                              
                if len(reg_ex) > 0 :
                    temp_start_year = int(re.findall(r'\d+', period)[0])

                    try:
                        temp_end_year = int(re.findall(r'\d+', period)[1])
                    except:
                        temp_end_year = "Present"
                        
                    start_years.append(temp_start_year)
                    end_years.append(temp_end_year)

                           
            # n_iter
            exp_len = len(companies)
            
            
            for i in range(exp_len):
            
                company = companies[i].find_all("span", {"class":"visually-hidden"})[0].text
                print(company)

                position = positions[i].find_all("span", {"class":"visually-hidden"})[0].text
                print(position)
                
                print(start_years[i], end_years[i])
               
                self.output_list.append((company, position, start_years[i], end_years[i]))
    
        else:
            
            for item_ind in range(len(self.exp_items)):
                
                temp_exp_items = self.exp_items[item_ind]
                
                temp_list = temp_exp_items.find_all("span", {"class":"mr1 hoverable-link-text t-bold"})
                
                
                ###############################################
                ### Case 1.1 - only single exp in a company ###
                ###############################################
                
                if len(temp_list) == 0:
                    
                    # position 
                    position = temp_exp_items.find_all("span", {"class":"mr1 t-bold"})[0].find("span",{"class":"visually-hidden"}).text

                    # company
                    company = temp_exp_items.find_all("span", {"class":"t-14 t-normal"})[0].find("span",{"class":"visually-hidden"}).text.split(" · ")[0]

                    # period 
                    period = temp_exp_items.find_all("span", {"class":"t-14 t-normal t-black--light"})[0].find("span",{"class":"visually-hidden"}).text.split(" · ")[0]

                    # start_year    
                    start_year =  int(re.findall(r'\d+', period)[0])

                    # end_year
                    try:
                        end_year =  int(re.findall(r'\d+', period)[1])
                    except:
                        end_year = "Present"

                    # append
                    print(company, position, start_year, end_year)

                    self.output_list.append((company, position, start_year, end_year))
                    
                    
                #############################################
                ### Case 1.2 - multiple exps in a company ###
                #############################################
                
                else:
                    temp_item = temp_exp_items.find_all("div", {"class":"display-flex align-items-center"})

                    # for the iteration in the for-loop below
                    temp_len = len(temp_item)

                    company_ind = 0 
                    company = temp_exp_items.find_all("div", {"class":"display-flex align-items-center"})[company_ind]
                    company = company.find_all("span", {"class":"visually-hidden"})[0].text

                    # periods
                    periods = temp_exp_items.find_all("span", {"class":"t-14 t-normal t-black--light"})

                    pos_ind, period_ind = 0,  0
                    
                    while True:

                        # position
                        position = temp_exp_items.find_all("div", {"class":"display-flex align-items-center"})[pos_ind]
                        position = position.find_all("span", {"class":"visually-hidden"})[0].text 

                        if position == company:

                            pos_ind += 1

                            position = temp_exp_items.find_all("div", {"class":"display-flex align-items-center"})[pos_ind]
                            position = position.find_all("span", {"class":"visually-hidden"})[0].text 


                        # period
                        temp_period = periods[period_ind].find_all("span", {"class":"visually-hidden"})[0].text.split(" · ")[0]

                        if len (re.findall(r'\d+',temp_period)) == 0:
                            period_ind +=1
                            temp_period = periods[period_ind].find_all("span", {"class":"visually-hidden"})[0].text.split(" · ")[0]


                        start_year = int(re.findall(r'\d+', temp_period)[0])

                        try:
                            end_year =  int(re.findall(r'\d+', temp_period)[1])
                        except:
                            end_year = "Present"

                        print(company, position, start_year, end_year)

                        self.output_list.append((company, position, start_year, end_year))

                        pos_ind += 1
                        period_ind +=1


                        if pos_ind == (temp_len):
                            break
                            
                            
        df_output = pd.DataFrame(self.output_list, columns = ["company","position","start_year","end_year"])
        df_output = df_output.sort_values(by=["start_year"])
        #df_output["user_id"] = self.profile_id
        #df_output = df_output[["user_id","company","position","start_year","end_year"]]

        return df_output

                    
    
    #############################################
    ### Case 2 - WITH "Show more experiences" ###        
    #############################################
        
    def case2_expand_exp(self):
        
        if self.exp_indicator:
            
            page_exp = self.driver.find_elements_by_xpath("//span[@class = 'pvs-navigation__text']")[self.exp_ind]

            # Y_coord of "show all experiences" button
            exp_y_cood = self.driver.find_elements_by_xpath("//span[@class = 'pvs-navigation__text']")[self.exp_ind].location["y"]

            self.driver.execute_script(f"window.scrollTo({exp_y_cood-1000},{exp_y_cood-500})")
            
            # click
            page_exp.click()
            
            # time sleep
            time.sleep(5)

            
    def case_2_button_parse(self):
        
        # time sleep
        time.sleep(5)
        
        # Parsing the clicked page
        self.expanded_html = self.driver.page_source
        self.expanded_soup = BeautifulSoup(self.expanded_html, 'lxml')

        self.expanded_items = self.expanded_soup.find_all("div",{"class":"pvs-entity pvs-entity--padded pvs-list__item--no-padding-when-nested"})
        
    
    def case_2_scraper(self):
        
        # output
        self.output_list = []
        
        for item_ind in range(len(self.expanded_items)):
            
            temp_exp_items = self.expanded_items[item_ind]
            
            temp_list = temp_exp_items.find_all("span", {"class":"mr1 hoverable-link-text t-bold"})
        
            ###############################################
            ### Case 2.1 - only single exp in a company ###
            ###############################################
            
            if len(temp_list) == 0: 

                # position 
                position = temp_exp_items.find_all("span", {"class":"mr1 t-bold"})[0].find("span",{"class":"visually-hidden"}).text

                # company
                company = temp_exp_items.find_all("span", {"class":"t-14 t-normal"})[0].find("span",{"class":"visually-hidden"}).text.split(" · ")[0]

                # period 
                period = temp_exp_items.find_all("span", {"class":"t-14 t-normal t-black--light"})[0].find("span",{"class":"visually-hidden"}).text.split(" · ")[0]

                # start_year    
                start_year =  int(re.findall(r'\d+', period)[0])

                # end_year
                try:
                    end_year =  int(re.findall(r'\d+', period)[1])
                except:
                    end_year = "Present"

                # append
                print(company, position, start_year, end_year)
                self.output_list.append((company, position, start_year, end_year))
                
            #############################################
            ### Case 2.2 - multiple exps in a company ###
            #############################################
            
            else:
        
                temp_item = temp_exp_items.find_all("div", {"class":"display-flex align-items-center"})

                # for the iteration in the for-loop below
                temp_len = len(temp_item)

                company_ind = 0 
                company = temp_exp_items.find_all("div", {"class":"display-flex align-items-center"})[company_ind]
                company = company.find_all("span", {"class":"visually-hidden"})[0].text

                # periods
                periods = temp_exp_items.find_all("span", {"class":"t-14 t-normal t-black--light"})

                pos_ind, period_ind = 0,  0

                while True:

                    # position
                    position = temp_exp_items.find_all("div", {"class":"display-flex align-items-center"})[pos_ind]
                    position = position.find_all("span", {"class":"visually-hidden"})[0].text 

                    if position == company:

                        pos_ind += 1

                        position = temp_exp_items.find_all("div", {"class":"display-flex align-items-center"})[pos_ind]
                        position = position.find_all("span", {"class":"visually-hidden"})[0].text 


                    # period
                    temp_period = periods[period_ind].find_all("span", {"class":"visually-hidden"})[0].text.split(" · ")[0]

                    if len (re.findall(r'\d+',temp_period)) == 0:
                        period_ind +=1
                        temp_period = periods[period_ind].find_all("span", {"class":"visually-hidden"})[0].text.split(" · ")[0]


                    start_year = int(re.findall(r'\d+', temp_period)[0])

                    try:
                        end_year =  int(re.findall(r'\d+', temp_period)[1])
                    except:
                        end_year = "Present"

                    print(company, position, start_year, end_year)

                    self.output_list.append((company, position, start_year, end_year))

                    pos_ind += 1
                    period_ind +=1


                    if pos_ind == (temp_len):
                        break

        df_output = pd.DataFrame(self.output_list, columns = ["company","position","start_year","end_year"])
        df_output = df_output.sort_values(by=["start_year"])
        #df_output["user_id"] = self.profile_id
        #df_output = df_output[["user_id","company","position","start_year","end_year"]]

        return df_output
    
 
#if __name__ == "__main__":
if __name__ == "__main__":
    print("xxx")
    
    
    

        


        
    


