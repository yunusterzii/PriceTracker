import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json

url = "https://public.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/sr?q=ak%C4%B1ll%C4%B1+telefon&qt=ak%C4%B1ll%C4%B1+telefon&st=ak%C4%B1ll%C4%B1+telefon&os=1&pi={}"
headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}


def getSoup(url, page):
    r = requests.get(url.format(page), headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    data = json.loads(soup.text)
    return data

def compareExcels(excel1, excel2):
    data = []
    df1 = pd.read_excel(excel1)
    df2 = pd.read_excel(excel2)
    for i in range(len((df1.index))):
        row = df1.iloc[i]
        description = row["description"]
        old_price = float(row["price"])

        newRow = df2.loc[(df2["description"] == description)]
        if not newRow.empty:
            new_price = float(newRow["price"].values[0])

            if old_price > new_price:
                # if (price - new_price) > (price/10):
                brand = newRow["brand"].values[0]
                description = newRow["description"].values[0]
                price = newRow["price"].values[0]
                sale_value = old_price - new_price
                sale = int((sale_value/old_price)*100)
                link = newRow["link"].values[0]
                
                data.append(
                    [brand, description, price, sale_value, sale, link])
                #if (old_price - new_price) > (old_price/10):

    appendExcel(data, "results.xlsx")


def writeExcel(data, filename):
    df = pd.DataFrame(
        data, columns=["brand", "description", "price", "link"])
    df.to_excel(filename, index=False)


def appendExcel(data, filename):
    df1 = pd.read_excel(filename)
    df2 = pd.DataFrame(
        data, columns=["marka", "açıklama", "fiyat", "indirim", "indirim oranı", "satıcı linki"])
    df3 = pd.concat([df1, df2])
    df3.to_excel(filename, index=False)

def getAllData(url, page, data_list):
    data = getSoup(url, page)
    total_product = int(data["result"]["roughTotalCount"])
    page_size = int(total_product // 24) + 1
    page_index = int(data["result"]["pageIndex"])
    for product in data["result"]["products"]:
            brand = product["brand"]["name"]
            name = product["name"]
            price = product["price"]["originalPrice"]
            link = product["url"]
            data_list.append([brand, name, price, link])
    if page_index < page_size:
        print(page)
        return getAllData(url, page+1, data_list)
    else:
        return data_list


if __name__ == '__main__':
    file1 = "./output1.xlsx"
    file2 = "./output2.xlsx" 
    while True:
        time1 = time.time()
        data = getAllData(url,1,[])
        if pd.read_excel(file1).empty:
            writeExcel(data, file1)
        else:
            writeExcel(data, file2)
            compareExcels(file1, file2)
            writeExcel(data, file1)
        time2 = time.time()
        print("Geçen süre " + str(time2 - time1))
        duration = 0.1
        print(str(duration)  + " dakika bekleniyor")
        time.sleep(duration*60)


