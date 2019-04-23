import mysql.connector
import requests
import re
from bs4 import BeautifulSoup
from sklearn import tree

def fetch():
    
    new_city = list()
    name_list = list()
    model_list = list()
    earning_list = list()
    city_list = list()
    price_list = list()
    cars_text = ""

    #Connect To SQL And Scraping ...
    con = mysql.connector.connect(user="root",password="",database="Cars",host="127.0.0.1")
    cursor = con.cursor()
    for i in range(150):
        cars_page = requests.get("https://bama.ir/car/all-brands/all-models/all-trims?page="+str(i))
        cars_text += cars_page.text
        soup = BeautifulSoup(cars_text,"html.parser")
        name = soup.findAll("span",attrs={"style":"display:inline-block;"})
        model = soup.findAll("h2",attrs={"class":"persianOrder"})
        earning = soup.findAll("p",attrs={"class":"price hidden-xs"})
        city = soup.findAll("span",attrs={"class":"provice-mobile"})
        price = soup.findAll("span",attrs={"itemprop":"price"})
        price = soup.findAll("p",attrs={"class":"cost"})

    #Scraping Name Of Cars
    for n in name:
        delspace_n = n.text.strip()
        regex_n = re.findall(r"^[^,.\[\]]+",delspace_n)
        joined_n = " ".join(regex_n)
        name_list.append(joined_n)

    #Scraping Model Of Cars
    for m in model:
        delspace_m = m.text.strip()
        regex_m = re.findall(r"^\d+",delspace_m)
        joined_m = " ".join(regex_m)
        model_list.append(joined_m)

    #Scraping Earning Of Cars
    for e in earning:
        delspace_e = e.text.strip()
        regex_e = re.findall(r"^.[^-]+",delspace_e)
        joined_e = " ".join(regex_e)
        earning_list.append(joined_e)

    #Scraping City Of Cars
    for c in city:
        delspace_c = c.text.strip()
        regex_c = re.findall(r".+",delspace_c)
        joined_c = " ".join(regex_c)
        city_list.append(joined_c)
    for i in city_list:
        if "،" not in i:
            city_list.remove(i)
    for j in city_list:
            new_city.append(str(j).replace("،",""))

    #Scraping Price Of Cars
    for p in price:
        delspace_p = p.text.strip()
        regex_p = re.findall(r".*",delspace_p)
        joined_p = " ".join(regex_p)
        price_list.append(joined_p)
    result = list(zip(name_list,model_list,earning_list,new_city,price_list))
    sql = "INSERT INTO scrap (name,model,earning,city,price) VALUES (%s,%s,%s,%s,%s)"
    for x in result:
        val = (x[0],x[1],x[2],x[3],x[4])
        cursor.execute(sql,val)
        cursor.execute("DELETE n1 FROM scrap n1,scrap n2 WHERE n1.id < n2.id AND n1.name = n2.name And n1.model = n2.model And n1.earning = n2.earning And n1.city = n2.city And n1.price = n2.price;")
        con.commit()
    con.close()


def ML():

    x = list()
    y = list()

    #Connecting To SQL
    value = input("Enter Name, Model, Earning And City :")
    list_value = value.split(",")
    con = mysql.connector.connect(user="root",password="",database="Cars",host="127.0.0.1")
    cursor = con.cursor()
    cursor.execute("SELECT name,model,earning,city,price FROM scrap")
    values = cursor.fetchall()
    for item in values:
        x.append(item[0:4])
        y.append(item[4])

    #Learning ...
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(x, y)

    #Predict Machine ...
    answer = clf.predict(list_value)
    print(answer)