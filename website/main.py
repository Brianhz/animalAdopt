from requests_html import HTMLSession
from flask import Flask

url = 'https://www.beerwulf.com/en-gb/c/beers?segment=Beers&catalogCode=Beer_1'

app = Flask(__name__)

@app.route("/")
def home():
    return "Home Page"

if __name__ == '__main__':
    app.run(debug=True, port=8000)


s = HTMLSession()
r = s.get(url)

r.html.render(sleep=1)


products = r.html.xpath('//*[@id="product-item-container"]', first=True)

for item in products.absolute_links: 
    r = s.get(item)
    name = r.html.find('div.product-detaili-info-title', first=True).text
    subtext =  r.html.find('div.product - subtext', first=True).text
    price =  r.html.find('span.price', first=True).text

    try:
        rating =  r.html.find('div.product - subtext', first=True).text
    except:
        rating = 'none'
    

    if r.html.find('div.add-to-cartcontainer'):
        stock = 'in stock'
    else:
        stock = 'out of stock'


    print(name, subtext, rating, price, stock)
    


