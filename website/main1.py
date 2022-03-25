from requests_html import HTMLSession
from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_admin import Admin 
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm, PostForm
from sqlalchemy import Column, String, Integer
from sqlalchemy import insert
import os

url = 'https://www.beerwulf.com/en-gb/c/beers?segment=Beers&catalogCode=Beer_1'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ggg'
admin = Admin(app)

@app.route('/')

@app.route("/home")
def home():
    #return "Home Page"#
    return render_template('p.html')

@app.route("/about")
def about():
    return render_template('About.html')

@app.route("/product")
def product():
    return render_template('Product.html')

@app.route("/account")
def account():
    return render_template('Account.html')

@app.route("/cart")
def cart():
    return render_template('Cart.html')

@app.route("/wanted")
def wanted():
    return render_template('Wanted.html')

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
    


