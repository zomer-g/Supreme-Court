import requests
from bs4 import BeautifulSoup
import csv

#parameters of the run
s_section = 1
e_section = 8

s_year = 2016
e_year = 2022

s_case = 1
e_case = 20



#Case_func receives a year, a running number, and a tab/section, and returns a dictionary containing titles and values of the specific case.
def case_func(year,case_n,section_n):
    #Parameter names fixed based on function
    case_id = str(case_n).zfill(6)
    section_id = f'menu{section_n}'

    URL =f'https://elyon2.court.gov.il/Scripts9/mgrqispi93.dll?Appname=eScourt&Prgname=GetFileDetails_for_new_site&Arguments=-N{year}-{case_id}-0'

    #Get the html text from the supreme Court site
    page = requests.get(URL)

    #There are some files that are encoded appropriately and some that are not
    soup = BeautifulSoup(page.content, "html.parser", from_encoding="iso-8859-8")
    results = soup.find(id=section_id)

    #Section 1 of the Supreme Court website has a different structure from Sections 2-7, so there are two separate parts.
    if results is not None:
        if section_n == 1:

            #File information fields are extracted
            menu1_dict={}
            #create unique name for each case
            t_list=[f'case_id_s']
            v_list =[f'{case_n}/{year}']
            menu1_list = []

            #Get list of all titles
            titles_m1 = results.find_all("span", class_="caseDetails-label")
            for title in titles_m1:
                t_list.append(title.text)

            #Get list of all values
            vals_m1 = results.find_all("span", class_="caseDetails-info")
            for val in vals_m1:
                v_list.append(val.text)

            #Create a dict with all the case level titles and values
            menu1_dict = dict(zip(t_list, v_list))
            if v_list!= []:
                menu1_list.append(menu1_dict)
            return menu1_list

        #for sections 2-6 (7 got bug)
        if section_n > 1 and section_n <= 7:
            titles_2 = []  # [f'case_id_s']
            for item in results.select("th"):
                titles_2.append(item.text.strip())

            values_2 = []  # [f'{case_n}/{year}']
            for item in results.select("td"):
                values_2.append(item.text.strip().replace('  ', '').replace('\r', ''))

            # Find the number of columns, lines and rounds of each table
            len_t = len(titles_2)
            len_v = len(values_2)
            rounds = int(len_v / len_t)

            # Create dictionary for each line in the table
            menu2_list = []
            for r in range(rounds):
                menu2_dict = {}

                list_r = []
                list_r += (values_2[r * len_t:(r + 1) * len_t])
                menu2_dict = dict(zip(titles_2, list_r))
                id_dict1 = {f'case_id_s': f'{case_n}/{year}'}
                menu2_dict.update(id_dict1)
                menu2_list.append(menu2_dict)
            return (menu2_list)



#the names of the sections in the Supreme-Court website, and later it will use them for the names of the CSV files
section_name= {1:'general_information', 2: 'parties', 3:'below', 4:'discussions', 5:'events', 6: 'confirmations', 7:'requests'}

#Runing the function on each table/section
for section in range(s_section,e_section):
    main_list = []
    # fails get +1 when the case is confidential or does not expire, so when the script reaches the last case of the year it gets continuous failures (8) and stops.
    fails = 0

    print(section_name[section])
    main_list = []

    # Select range of years to run on
    for year in range(s_year, e_year):
        print(year)

        #For each section, running the function on each case
        for case in range(s_case, e_case):

            # An empty dictionary condition is intended for confidential cases
            if case_func(year, case, section) is not None:
                fails = 0
                main_list+=(case_func(year, case, section))
            else:
                fails += 1
            if fails == 8:
                break
            print (case)



    #Export to csv all the cases data
    to_csv = main_list
    keys = to_csv[0].keys()
    csv_name = section_name[section]+'.csv'
    with open(csv_name, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(to_csv)
        output_file.close()


