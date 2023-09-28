import requests
from bs4 import BeautifulSoup
import json

url = 'https://999.md/ro/84184547'
def get_data(url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            #print(soup)
            data = {
                "title": soup.title.string,
                "descriere":" ",
                "general": [],
                "particularitati": "",
                "subcategorie": "",
                "preț": "",
                "regiunea": "",
                "contacte": []
            }
            #get description
            descrip = soup.find("div", class_="adPage__content__description grid_18", itemprop="description")
            data["descriere"] = descrip.get_text(strip=True)
            #print(data["descriere"])

            #get general caracteristics
            list = soup.find("div", class_="adPage__content__features__col grid_9 suffix_1")
            el = list.find("ul")
            general= el.find_all("li", class_="m-value")
            element_general = []
            for item in general:
                key = item.find("span", class_="adPage__content__features__key").get_text(strip=True)
                value = item.find("span", class_="adPage__content__features__value").get_text(strip=True)
                element_general.append({key: value})
            data["general"] = element_general

            #get particularitati
            part= soup.find("div", class_="adPage__content__features__col grid_7 suffix_1")
            elem = part.find("ul")
            part_data = elem.find_all("li", class_="m-value")

            list_particularitati = []
            for item in part_data:
                key = item.find("span", class_="adPage__content__features__key").get_text(strip=True)
                value = item.find("span", class_="adPage__content__features__value").get_text(strip=True)
                list_particularitati.append({key: value})
            data["particularitati"] = list_particularitati

            #get subcategorie
            subcat = soup.find("a", class_="adPage__content__features__category__link")
            data["subcategorie"] = subcat.get_text(strip=True)

            #get pret
            pret = soup.find("ul", class_="adPage__content__price-feature__prices")
            data["preț"] = pret.get_text(strip=True)

            #get regiune
            region= soup.find("dl", class_="adPage__content__region grid_18")
            name = region.get_text(strip=True)
            data["regiunea"] = name.replace("Regiunea:", "").strip()

            #get contacte
            contacts= soup.find("dl", class_="js-phone-number adPage__content__phone is-hidden grid_18")
            c=contacts.get_text(strip=True)
            data["contacte"] = c.replace("Contacte:", "").strip()

            info = json.dumps(data, indent=4, ensure_ascii=False)
            with open("data.json", "w", encoding="utf-8") as file:
                file.write(info)
            data_list=info.encode('utf-8').decode('utf-8')

        else:
            print("Something went wrong")
        return data_list

if __name__ == "__main__":
    data_list=get_data(url)
    print(data_list)
   