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

    #There are some files that are encoded appropriately and some that are not
    soup = BeautifulSoup(page.content, "html.parser", from_encoding="iso-8859-8")
    results = soup.find(id=section_id)

    if results is not None:
        if section_n == 1:

            #File information fields are extracted
            menu1_dict={}
            t_list=[f'case_id_s']
            v_list =[f'{case_n}/{year}']

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

            return (menu1_dict)

        if section_n > 1 and section_n <= 7:
            t2_list = [f'case_id_s']
            v2_list = [f'{case_n}/{year}']
            menu2_dict = {}


            for th in results.find_all("th"):
                t2_list.append(th.text.replace('  ', '').replace('\r', '').replace('\n', ''))
            for td in results.find_all("td"):
                v2_list.append(td.text.replace('  ', '').replace('\r', '').replace('\n', ''))

            lines = int(len(v2_list) / len(t2_list))
            long = int(len(t2_list))

            for l in range(lines):
                v2_list_cut = v2_list[long * (l):long * (l + 1)]
                menu2_dict = dict(zip(t2_list, v2_list_cut))
                if menu2_dict != {}:
                    return (menu2_dict)

        else:
            return ('This section is not available')

section_name= {1:'general_information', 2: 'parties', 3:'below', 4:'discussions', 5:'events', 6: 'confirmations', 7:'requests'}

for section in range(1,8):

    main_list = []

    # fails get +1 when the case is confidential or does not expire, so when the script reaches the last case of the year it gets continuous failures (8) and stops.
    fails = 0

    for i in range(1, 4):
        # An empty dictionary condition is intended for confidential cases
        if case_func(2022, i, section) is not None:
            fails = 0
            main_list.append(case_func(2022, i, section))
        else:
            fails += 1
        if fails == 8:
            break



    # Export to csv all the cases data
    to_csv = main_list
    keys = to_csv[0].keys()
    csv_name = section_name[section]+'.csv'
    with open(csv_name, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(to_csv)
        output_file.close()


