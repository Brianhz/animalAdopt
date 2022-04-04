from fileinput import filename
from unicodedata import decomposition
from requests_html import HTMLSession
from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_admin import Admin 
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user
from forms import RegistrationForm, LoginForm, PostForm, LostForm
from sqlalchemy import Column, String, Integer
from sqlalchemy import insert
from werkzeug.utils import secure_filename
import os
import mimetypes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ggg'
admin = Admin(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author',lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    #def __init__(self, id, username, email, image_file, password):
    #    self.id = id
    #    self.username = username
    #    self.email = email
    #    self.image_file = image_file
    #    self.password = password

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    credit_No = db.Column(db.String(21), nullable=False)


    def __repr__(self):
        return f"Session('{self.username}', '{self.sid}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False) 
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}'):"

class Lost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_lostposted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    desciption = db.Column(db.Text, nullable=False)
    img = db.Column(db.Text, nullable=False) 
    mimetype = db.Column(db.Text, nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_lostposted}'):"

class Product(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=False)

    def __init__(self, pid, title, price, image):
        self.pid = pid
        self.title = title
        self.price = price
        self.image = image

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    comment = db.Column(db.Text)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer)
    product_name = db.Column(db.String(20))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)


posts = [
    {
        'author': 'Ccc',
        'title': 'Blog Post1',
        'content': 'First post content',
        'date_posted': 'April 21, 2020'
    },
    {
    
        'author': 'HHH',
        'title': 'Good shop',
        'content': 'it is a really good shop with different brands',
        'date_posted': 'April 29, 2021'
    }
]
@app.route('/')

@app.route('/pay')
def pay():
    return render_template("cashier.html")
@app.route('/cashier', methods=['GET', 'POST'])
def cashier():
    if request.method == "POST":
        credit_No = request.values.get("credit_No")
        if credit_No != None:
            print(credit_No)
            credit = Payment(credit_No=credit_No)
            db.session.add(credit)
            db.session.commit()
            carts = session["cart"]
            user_id = session["user_id"]
            if carts != None and user_id != None:
                for x1 in carts:
                    ordersRec = Orders(user_id=user_id, product_id=x1["product"], product_name=x1["productTitle"], quantity=x1["quantity"], price=x1["unitPrice"])
                    db.session.add(ordersRec)
                    db.session.commit()
            flash(f"Thank you for your purchase!!")
            return redirect(url_for('home'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        product = request.values.get("search")
        print(product)
        #productList = Product.query.filter_by(title=product)
        productList = Product.query.filter(Product.title.like("%{}%".format(product)))
        if productList == None:
            print("cannot find the required product")
            flash("cannot find the required product")
        return render_template("Product.html", productList=productList )

    return render_template('product.html')



@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/addrec')
def addrec():
    ballGreenN = Product(1, 'ballGreenNike', 10, 'ballGreenNike.jpg')
    ballOrangeA = Product(2, 'ballOrangeAdidas', 12, 'ballOrangeAdidas.jpg')
    ballWhiteN = Product(3, 'ballWhiteNike', 23, 'ballWhiteNike.jpg')
    ballpack = Product(4, 'ballpack', 11, 'ballpack.jpg')
    db.session.add(ballGreenN)
    db.session.add(ballWhiteN)
    db.session.add(ballOrangeA)
    db.session.add(ballpack)
#    db.session.commit()
    print("db insert end")
    return render_template("p.html", posts=posts)

@app.route('/product')
def product():
    # This page shows all products
    productList = Product.query.all()
    return render_template("Product.html", productList=productList )

@app.route("/item/<int:id>")
def display_item(id):
    # This page show one product. Customer can add it to cart
    item = Product.query.filter_by(pid=id).first()

    # <<< debug
    print(item.pid)
    print(item.title)
    print(item.price)
    print(item.image)
    # >>> debug

    return render_template("Item.html", display_item=item)

@app.route('/add_to_cart/<int:id>',methods=["GET", "POST"])
def add_to_cart(id):
    quantity = request.values.get("quantity")
    productTitle = request.values.get("productTitle")
    unitPrice = request.values.get("unitPrice")
    print(id)
    print(quantity)
    print(productTitle)
    print(unitPrice)
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append({"product":id, "productTitle": productTitle, "quantity":quantity, "unitPrice": unitPrice})
    #print session[cart]
    flash("Successfully added to cart!")
    return redirect("/cart")

@app.route('/p')
def p():
    # return render_template('p.html')
    return render_template('p.html')

@app.route("/home")
def home():
    #return "Home Page"#
    return render_template('Home.html')

@app.route("/about")
def about():
    if request.method == "POST":
        if 'user_id' in session:
            commentStr = request.values.get("comment")
            userId = session['user_id']
            commentRec = Comment(user_id=userId, comment=commentStr)
            db.session.add(commentRec)
            db.session.commit()
            flash("thank you for your comments")
            return redirect(url_for('about'))
        else:
            flash("Please login")
            return redirect(url_for('account'))

    form=PostForm()

    return render_template("About.html", posts=posts, form=form)

@app.route('/comment' , methods=["GET", "POST"])
def submitComment():
    if request.method == "POST":
       if  "username" in session:
        commentStr = request.values.get("comment")
        userId = session['user_id']
        commentRec = Comment(user_id=userId, comment=commentStr)
        db.session.add(commentRec)
        db.session.commit()
        flash("thank you for your comments")
        return redirect(url_for('about'))
       else:
          return redirect(url_for('account'))
    else:
        return "GET comment"

@app.route('/blog',methods=["GET", "POST"])
def writeBlog():
    if request.method == "POST":
       if  "username" in session:
        email = request.values.get("email")
        title = request.values.get("title")
        content = request.values.get("content")
        user_id = session['user_id']
        blogRec = Post(user_id=user_id, title=title, content=content, email=email)
        db.session.add(blogRec)
        db.session.commit()
        blogs = Post.query.all()
        form=PostForm()
        return render_template("About.html", blogs=blogs, form=form, posts=posts)
       else:
          return redirect(url_for('account'))
    else:
        return "GET blog"


@app.route("/account")
def account():
    error = None
    if request.method == "POST":
        username = request.values.get("username")
        password = request.values.get("password")

        # debug
        print(username)
        print(password)

        userRec = User.query.filter_by(username=username, password=password).first()

        if userRec != None:
            print(userRec.email)
            session['username'] = request.form['username']
            session['user_id'] = userRec.id
            return redirect(url_for('home'))
        else:
            print("record not found")
            flash("Invalid username/password: " + username + "/" + password)
            error = "Username / Passord: " + username + "/" + password + " not found!!"

    if 'username' in session:
        session.pop('username', None)
        return render_template('p.html', posts=posts)
    else:
        return render_template('Account.html', posts=posts)

@app.route('/register',methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.values.get("username")
        password = request.values.get("password")
        confirm_password = request.values.get("confirm_password")
        email = request.values.get("email")

        print(password)
        print(confirm_password)
        print(email)
        
        name = User.query.filter_by(username=username).first()
        user_email =  User.query.filter_by(email=email).first()
        
        if name == None:
            if user_email == None:
                if password == confirm_password:
                    new_user = User(username=username, password=confirm_password, email=email)
                    print(new_user)
                    db.session.add(new_user)
                    db.session.commit()
                    flash(f"user created {username} !!")
                    return redirect(url_for('account'))
                else:
                    flash('wrong password')
            else:
                flash(" this email  has been taken ")
                return redirect(url_for('register'))
        else:
            flash(" this username has been taken ")
            return redirect(url_for('register'))

                
    
    return render_template("Register.html", posts=posts)

@app.route("/admin")
@login_required
def admin():
    id = current_user.id
    if id == "1":
         return render_template("admin.html")
    else:
        flash("Sorry you must be Admin")
        return render_template("p.html")

@app.route("/cart")
def cart():
    if 'user_id' in session:
        userId = session['user_id']
    else:
          flash("Please login")
          return redirect(url_for('account'))
    return render_template("Cart.html", posts=posts)
    #return render_template('Cart.html')

@app.route("/wanted",methods=["GET", "POST"])
def wanted():
    if request.method == "POST":
        if  "username" in session:
         title = request.values.get("title")
         desciption = request.values.get("descriiption")
         user_id = session['user_id']
         pic = request.files['pic']
         filename = secure_filename(pic.filename)
         mimetype = pic.mimetype
         lostRec = Post(user_id=user_id, title=title, desciption=desciption, pic=pic, img=pic.read(), mimetype=mimetype)
         db.session.add(lostRec)
         db.session.commit()
         lost = Post.query.all()
         form=LostForm()
         return render_template("Wanted.html", lost=lost, form=form, posts=posts)
        else:
          return redirect(url_for('account'))
    else:
        return render_template("Wanted.html")
        #return "GET wanted"





if __name__ == '__main__':
        app.run(debug=True, port=8000)

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Lost, db.session))
admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(Payment, db.session))
admin.add_view(ModelView(Comment, db.session))
admin.add_view(ModelView(Orders, db.session))

if not os.path.exists('site.db'):
    db.create_all()
 
else:
    app.run(debug=True)

#s = HTMLSession()
#r = s.get(url)

# r.html.render(sleep=1)


#products = r.html.xpath('//*[@id="product-item-container"]', first=True)

# for item in products.absolute_links: 
#     r = s.get(item)
#     name = r.html.find('div.product-detaili-info-title', first=True).text
#     subtext =  r.html.find('div.product - subtext', first=True).text
#     price =  r.html.find('span.price', first=True).text

#     try:
#         rating =  r.html.find('div.product - subtext', first=True).text
#     except:
#         rating = 'none'
    

#     if r.html.find('div.add-to-cartcontainer'):
#         stock = 'in stock'
#     else:
#         stock = 'out of stock'


#     print(name, subtext, rating, price, stock) 
    


