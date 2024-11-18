import pymongo
from bs4 import BeautifulSoup

#mongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["web_crawler"]
pages_collection = db["pages"]
professors_collection = db["professors"]

def parse_faculty_info():
    #gets target
    page_data = pages_collection.find_one({"html": {"$exists": True}})
    if not page_data:
        print("No page data found in the database")
        return
    
    soup = BeautifulSoup(page_data["html"], "html.parser")

    faculty_members = soup.find_all("div", class_="faculty-member")

    for member in faculty_members:
        name = member.find("h2").get_text(strip=True)
        title = member.find("p", class_="title").get_text(strip=True)
        office = member.find("p", class_="office").get_text(strip=True)
        phone = member.find("p", class_="phone").get_text(strip=True)
        email = member.find("a", href=lambda href: href and "mailto" in href).get_text(strip=True)
        website = member.find("a", href=lambda href: href and href.startswith("http"))["href"]

        #storing
        professors_collection.insert_one({
            "name": name,
            "title": title,
            "office": office,
            "phone": phone,
            "email": email,
            "website": website
        })

if __name__ == "__main__":
    parse_faculty_info()