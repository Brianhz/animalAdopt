from requests_html import HTMLSession

url = 'https://www.beerwulf.com/en-gb/c/beers?segment=Beers&catalogCode=Beer_1'


s = HTMLSession()
r = s.get(url)

r.html.render(sleep=1)

products = r.html.xpath('//*[@id="product-item-container"]', first=True)

for item in products.absolute_links: 
    r = s.get(item)
    print(r.html.find('div.product-detaili-info-title', first=True).text)
    
    https://www.youtube.com/watch?v=gW-q6G9KYTg