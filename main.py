import requests
from bs4 import BeautifulSoup
import csv

#Case_func receives a year, a running number, and a tab (currently works only with tab 1), and returns a dictionary containing titles and values of the specific case.
def case_func(year,case_n,section_n):
    #Parameter names fixed based on function
    case_id = str(case_n).zfill(6)
    section_id = f'menu{section_n}'
    URL =f'https://elyon2.court.gov.il/Scripts9/mgrqispi93.dll?Appname=eScourt&Prgname=GetFileDetails_for_new_site&Arguments=-N{year}-{case_id}-0'

    #Get the html text from the supreme Court site
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id=section_id)

    #File information fields are extracted
    menu1_dict={}
    t_list=[]
    v_list =[]

    #Get list of all titles
    titles = results.find_all("span", class_="caseDetails-label")
    for title in titles:
        t_list.append(title.text)

    #Get list of all values
    vals = results.find_all("span", class_="caseDetails-info")
    for val in vals:
        v_list.append(val.text)

    #Create a dict with all the case level titles and values
    menu1_dict = dict(zip(t_list, v_list))
    return(menu1_dict)

#Make a list of all cases dictionaries
cases_list=[]
for i in range(1,2):
    cases_list.append(case_func(2022,i,1))S

#print(cases_list)

#Export to csv all the cases data
to_csv = cases_list
keys = to_csv[0].keys()
with open('court_cases.csv', 'w', newline='', encoding='utf-8') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(to_csv)
    output_file.close()
