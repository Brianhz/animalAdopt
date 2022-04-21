from email.policy import default
from fileinput import filename
from unicodedata import decomposition
import flask_login
from requests_html import HTMLSession
from datetime import datetime, date
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_admin import Admin 
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user, LoginManager, login_user, UserMixin, logout_user
from forms import RegistrationForm, LoginForm, PostForm, LostForm
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy import insert, update, delete
from sqlalchemy import Table, literal_column
from werkzeug.utils import secure_filename
from django.shortcuts import get_object_or_404
import os
import smtp
from flask import make_response
from io import BytesIO
import base64
import random
import math


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ggg'
admin = Admin(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Define upload folder
UPLOAD_FOLDER = 'upload_img'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


### Define database structure: User, Payment, Posts, Lost, Product, Comment, Orders
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(220), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Posts', backref='author',lazy=True)

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
        # return f"Session('{self.username}', '{self.sid}')"
        return f"Payment('{self.username}', '{self.sid}')"

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False) 
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(100))
    pic =  db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Posts('{self.title}', '{self.date_posted}'):"

class Lost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_lostposted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    filename = db.Column(db.Text, nullable=False) 
    img = db.Column(db.Text, nullable=False) 
    mimetype = db.Column(db.Text, nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Lost('{self.title}', '{self.date_lostposted}'):"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Product('{self.title}','{self.price}','{self.image}'):"

class Adopt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dob = db.Column(db.DateTime, nullable=False)
    petType = db.Column(db.String, nullable=False)
    ptt = db.Column(db.String, nullable=False)
    title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, default=0)
    image = db.Column(db.String(100), nullable=False)
    adopted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Adopt('{self.dob}','{self.petType}','{self.ptt}','{self.title}', '{self.description}', '{self.price}', '{self.image}'):"

    # def __init__(self, id, title, description, price, image, adopted):
    #     self.id = id
    #     self.title = title
    #     self.description = description
    #     self.price = price
    #     self.image = image
    #     self.adopted = adopted

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    date_comment = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Comment('{self.user_id}','{self.comment}'):"

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer)
    product_name = db.Column(db.String(20))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    date_order = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    def __repr__(self):
        return f"Order('{self.user_id}','{self.product_id}','{self.quantity}', '{self.price}'):"

# Create tables 
if not os.path.exists('site.db'):
    db.create_all()
else:
    app.run(debug=True)

# Pre-input posts record in table Posts
# posts = [
#     {
#         'author': 'Ccc',
#         'title': 'Blog Post1',
#         'content': 'First post content',
#         'date_posted': 'April 21, 2020'
#     },
#     {
    
#         'author': 'HHH',
#         'title': 'Good shop',
#         'content': 'it is a really good shop with different brands',
#         'date_posted': 'April 29, 2021'
#     }
# ]

# new_product1 = Product(title="dog1", price="55", image="dog1.jpg")
# db.session.add(new_product1)
# db.session.commit()
# new_product2 = Product(title="dog2", price="66", image="dog2.jpg")
# db.session.add(new_product2)
# db.session.commit()
# new_product3 = Product(title="dog2", price="77", image="dog3.jpg")
# db.session.add(new_product3)
# db.session.commit()
# new_product4 = Product(title="dog4", price="44", image="dog4.jpg")
# db.session.add(new_product4)
# db.session.commit()
# new_product5 = Product(title="dog5", price="66", image="dog5.jpg")
# db.session.add(new_product5)
# db.session.commit()
# new_product6 = Product(title="dog6", price="51", image="dog6.jpg")
# db.session.add(new_product6)
# db.session.commit()

# new_posts1 = Posts(user_id=1, email="asd@asd.com", title="Blog Post1", content="1st post content")
# db.session.add(new_posts1)
# db.session.commit()
# new_posts2 = Posts(user_id=2, email="asd2@asd.com", title="Good shop", content="it is a really good shop with different brands!")
# db.session.add(new_posts2)
# db.session.commit()

# db.session.query(Adopt).delete()
# db.session.commit()

# new_adopt1 = Adopt(dob = datetime.strptime("22/10/20", '%y/%m/%d'), ptt = "CT", petType = "dog", title="test1", description="test1", price=0, image="download-1.jpg")
# db.session.add(new_adopt1)
# db.session.commit()
# new_adopt2 = Adopt(dob = datetime.strptime("22/10/10", '%y/%m/%d'), ptt = "KT", petType = "dog", title="test2", description="test2", price=0, image="download-2.jpg")
# db.session.add(new_adopt2)
# db.session.commit()
# new_adopt3 = Adopt(dob = datetime.strptime("22/12/05", '%y/%m/%d'), ptt = "YMT", petType = "dog", title="test3", description="test3", price=0, image="download-3.jpg")
# db.session.add(new_adopt3)
# db.session.commit()
# new_adopt4 = Adopt(dob = datetime.strptime("22/11/20", '%y/%m/%d'), ptt = "CT", petType = "dog", title="test4", description="test4", price=0, image="download-4.jpg")
# db.session.add(new_adopt4)
# db.session.commit()
# new_adopt5 = Adopt(dob = datetime.strptime("22/12/10", '%y/%m/%d'), ptt = "KT", petType = "dog", title="test5", description="test5", price=0, image="download-5.jpg")
# db.session.add(new_adopt5)
# db.session.commit()
# new_adopt6 = Adopt(dob = datetime.strptime("22/12/25", '%y/%m/%d'), ptt = "YMT", petType = "dog", title="test6", description="test6", price=0, image="download-6.jpg")
# db.session.add(new_adopt6)
# db.session.commit()




# Define admin view of db
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Posts, db.session))
admin.add_view(ModelView(Lost, db.session))
admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(Payment, db.session))
admin.add_view(ModelView(Adopt, db.session))
admin.add_view(ModelView(Comment, db.session))
admin.add_view(ModelView(Orders, db.session))

# Define route
@app.route('/')
def home():
    return render_template("p.html")


@app.route('/pay')
def pay():
    print("/pay ...")
    return render_template("cashier.html")

@app.route('/adopt', methods=['GET', 'POST'] )
def adopt():
    if (request.method == "POST" or request.method == "GET"):
        adoptlist = Adopt.query.filter_by(adopted = False)
        return render_template("Adopt.html", adoptlist=adoptlist)
    else:
        return render_template("p.html")

# @app.route('/adopt_submit/<adoptitem_id>', methods=['GET', 'POST'] )
# def adopt_submit(adoptitem_id):
#     stmt = (
#     update(Adopt).
#     where(Adopt.id == adoptitem_id).
#     values(adopted = True)
#     )
#     db.session.execute(stmt)
#     db.session.commit()

#     if "username" in session:
#         username = session['username']
#         userRec = User.query.filter_by(username=username).first()
#         user_id = userRec.id
#         product_id = adoptitem_id
#         adoptRec = Adopt.query.filter_by(id=adoptitem_id).first()
#         if adoptRec != None:
#             product_name = adoptRec.title
#             ordersRec = Orders(user_id=user_id, product_id=product_id, product_name=product_name, quantity=1, price=0)
#             db.session.add(ordersRec)
#             db.session.commit()

#     adoptlist = Adopt.query.filter_by(adopted = False)
#     return render_template("Adopt.html", adoptlist=adoptlist)

@app.route('/adopt_submit/<adoptitem_id>', methods=['GET', 'POST'] )
def adopt_submit(adoptitem_id):
    stmt = (
    update(Adopt).
    where(Adopt.id == adoptitem_id).
    values(adopted = True)
    )
    db.session.execute(stmt)
    db.session.commit()

    if "username" in session:
        print("adopt_submit")
        username = session['username']
        userRec = User.query.filter_by(username=username).first()
        user_id = userRec.id
        product_id = adoptitem_id
        adoptRec = Adopt.query.filter_by(id=adoptitem_id).first()           
        product_name = adoptRec.title
        if "cart" not in session:
            session["cart"] = []        
        cartLen = len(session['cart'])
        cartLenStr = "id" + str(cartLen) + "id-adopt"
        cartList = session["cart"]
        cartList.append({"product":adoptitem_id, "productTitle": product_name, "quantity": 1, "unitPrice": 0, "id":cartLenStr})
        session["cart"] = cartList
        # session["cart"].append({"product":adoptitem_id, "productTitle": product_name, "quantity": 1, "unitPrice": 0, "id":cartLenStr})


    adoptlist = Adopt.query.filter_by(adopted = False)
    return render_template("Adopt.html", adoptlist=adoptlist)

# @app.route('/add_to_cart/<int:pid>',methods=["GET", "POST"])
# def add_to_cart(pid):
#     print("add_to_cart")
#     quantity = request.values.get("quantity")
#     productTitle = request.values.get("productTitle")
#     unitPrice = request.values.get("unitPrice")
#     print(pid)
#     print(quantity)
#     print(productTitle)
#     print(unitPrice)
#     if "cart" not in session:
#         session["cart"] = []
#     cartLen = len(session['cart'])
#     cartLenStr = "id" + str(cartLen) + "id"
#     session["cart"].append({"product":pid, "productTitle": productTitle, "quantity":quantity, "unitPrice": unitPrice, "id":cartLenStr})

#     #print session[cart]
#     flash("Successfully added to cart!")
#     print("Successfully added to cart!")
#     # return redirect("/cart")
#     return redirect(url_for("cart"))



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
            session.pop('cart', None)
            return redirect(url_for('p'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        product = request.values.get("search")
        print(product)
        #productList = Product.query.filter_by(title=product)
        productList = Product.query.filter(Product.title.like("%{}%".format(product)) | Product.price.like("%{}%".format(product)))
        if productList == None:
            print("cannot find the required product")
            flash("cannot find the required product")
        return render_template("Product.html", productList=productList )

    return render_template('product.html')\

# @app.route('/search_comment', methods=['GET', 'POST'])
# def search_comment():
#     if request.method == "POST":
#         comment = request.values.get("search_comment")
#         print("abc")
#         print(comment)
#         #commentList = Comment.query.filter_by(user_id=user_id)
#         commentList = Comment.query.filter(Comment.user_id.like("%{}%".format(comment)))
#         if commentList == None:
#             print("cannot find the required user_id")
#             flash("cannot find the required user_id")
#         else:
#             print("bbc")
#             for comment1 in commentList:
#                 print(comment1)           
#         return render_template("admin_Comment.html", commentList=commentList )
#     else:
#         return render_template('admin_Comment.html')

# @app.route('/search_order', methods=['GET', 'POST'])
# def search_order():
#     if request.method == "POST":
#         order = request.values.get("search_order")
#         print("abc")
#         print(order)
#         #commentList = Comment.query.filter_by(user_id=user_id)
#         orderList = Orders.query.filter(Orders.user_id.like("%{}%".format(order)))
#         if orderList == None:
#             print("cannot find the required user_id")
#             flash("cannot find the required user_id")
#         else:
#             print("bbc")
#             for order1 in orderList:
#                 print(order1)           
#         return render_template("admin_Order.html", orderList=orderList )
#     else:
#         return render_template("admin_Order.html")

@app.route('/logout')
def logout():
    print("logout...")
    logout_user()
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('cart', None)
    flash('You were logged out')
    return redirect(url_for('p'))

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
    return render_template("p.html")

@app.route('/product')
def product():
    # This page shows all products
    productList = Product.query.all()
    return render_template("Product.html", productList=productList )

@app.route("/item/<int:id>")
def display_item(id):
    # This page show one product. Customer can add it to cart
    item = Product.query.filter_by(id=id).first()

    # <<< debug
    print(item.id)
    print(item.title)
    print(item.price)
    print(item.image)
    # >>> debug

    return render_template("Item.html", display_item=item)

@app.route('/add_to_cart/<int:pid>',methods=["GET", "POST"])
def add_to_cart(pid):
    print("add_to_card")
    quantity = request.values.get("quantity")
    productTitle = request.values.get("productTitle")
    unitPrice = request.values.get("unitPrice")
    print(pid)
    print(quantity)
    print(productTitle)
    print(unitPrice)
    if "cart" not in session:
        session["cart"] = []
    cartLen = len(session['cart'])
    cartLenStr = "id" + str(cartLen) + "id-animal"
    session["cart"].append({"product":pid, "productTitle": productTitle, "quantity":quantity, "unitPrice": unitPrice, "id":cartLenStr})

    #print session[cart]
    flash("Successfully added to cart!")
    print("Successfully added to cart!")
    # return redirect("/cart")
    return redirect(url_for("cart"))

@app.route('/p')
def p():
    # return render_template('p.html')
    return render_template('p.html')

# @app.route("/home")
# def home():
#     #return "Home Page"#
#     # return render_template('Home.html')
#     return render_template('p.html')

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

    return render_template("About.html", form=form)

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

@app.route("/admin1")
@login_required
def admin1():
    id = current_user.id
    if id is None:
        print("id is None")
    else:
        print("id: " + str(id))
    if id == 1:
         return render_template("admin.html")
    else:
        # return render_template("customer.html")
        print("Sorry you must be Admin")
        flash("Sorry you must be Admin")
        return render_template("p.html")

@app.route('/admin_Comment',methods=["GET", "POST"])
def admin_Comment():
    print('displaycomment')
    comment = request.values.get("admin_Comment")
    if comment == None:
        commentList = Comment.query.all()
    else:
        commentList = Comment.query.filter(Comment.user_id.like("%{}%".format(comment)) | Comment.comment.like("%{}%".format(comment)) | Comment.date_comment.like("%{}%".format(comment)))        
    return render_template("admin_Comment.html", commentList=commentList )


@app.route('/admin_Order',methods=["GET", "POST"])
def admin_Order():
    print('displayorder')
    order = request.values.get("admin_Order")
    # order2 = request.values.get("admin_Order")
    if order == None:
        orderList = Orders.query.all()
    else:
        orderList = Orders.query.filter(Orders.user_id.like("%{}%".format(order)) | Orders.product_id.like("%{}%".format(order))| Orders.product_name.like("%{}%".format(order))| Orders.quantity.like("%{}%".format(order))| Orders.price.like("%{}%".format(order))| Orders.date_order.like("%{}%".format(order)))        
    return render_template("admin_Order.html", orderList=orderList )

@app.route("/index")
def index():
    print('displayorder2')
    order = request.values.get("admin_Order")
    # order2 = request.values.get("admin_Order")
    if order == None:
        orderList = Orders.query.all()
    else:
        orderList = Orders.query.filter(Orders.user_id.like("%{}%".format(order)) | Orders.product_id.like("%{}%".format(order))| Orders.product_name.like("%{}%".format(order))| Orders.quantity.like("%{}%".format(order))| Orders.price.like("%{}%".format(order))| Orders.date_order.like("%{}%".format(order))) 
    return render_template("index.html", orderList=orderList)

@app.route('/deleteOrder/<int:id>',methods=["GET", "POST"])
def deleteOrder(id):
    print('displayorder')
    order = Orders.query.get_or_404(id)
    print('1')
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('admin_Order'))

@app.route('/deleteOpinion/<int:id>',methods=["GET", "POST"])
def deleteOpinion(id):
    print('displayorder')
    comment = Comment.query.get_or_404(id)
    print('1')
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('admin_Comment'))

@app.route('/customerdeleteOrder/<int:id>',methods=["GET", "POST"])
def customerdeleteOrder(id):
    print('displayorder')
    order = Orders.query.get_or_404(id)
    print('1')
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('customer_Order'))

@app.route('/customerdeleteLost/<int:id>',methods=["GET", "POST"])
def customerdeleteLost(id):
    print('displayorder')
    lost = Lost.query.get_or_404(id)
    print('1')
    db.session.delete(lost)
    db.session.commit()
    return redirect(url_for('customer_Lost'))



@app.route("/customer")
# @login_required
def customer():
    print('a')
    return render_template("Customer.html")


@app.route('/customer_Order',methods=["GET", "POST"])
def customer_Order():
    print('displayorder')
    id = session['user_id']
    print("id : " + str(id))
    order = request.values.get("customer_Order")
    if order == None:
        print(" order == None")
        orderList = Orders.query.filter_by(user_id=id)
    else:
        print(" order == None else")
        orderList = Orders.query.filter(Orders.id.like("%{}%".format(order)))        
    return render_template("customer_Order.html", orderList=orderList )




@app.route('/customer_Lost',methods=["GET", "POST"])
def customer_Lost():
    id = session['user_id']
    print('displaycomment')
    lost = request.values.get("customer_Lost")
    if lost == None:
        print("1")
        lostList = Lost.query.filter_by(user_id=id)
        print("2")
    else:
        lostList = Lost.query.filter(Lost.id.like("%{}%".format(lost)))        
    return render_template("customer_Lost.html", lostList=lostList )



#     @app.route('/search_order', methods=['GET', 'POST'])
#    def search_order():
#     if request.method == "POST":
#         order = request.values.get("search_order")
#         if 
#         print("abc")
#         print(order)
#         #commentList = Comment.query.filter_by(user_id=user_id)
#         orderList = Orders.query.filter(Orders.user_id.like("%{}%".format(order)))
#         if orderList == None:
#             print("cannot find the required user_id")
#             flash("cannot find the required user_id")
#         else:
#             print("bbc")
#             for order1 in orderList:
#                 print(order1)           
#         return render_template("admin_Order.html", orderList=orderList )
#     else:
#         return render_template("admin_Order.html")


@app.route('/blog',methods=["GET", "POST"])
def writeBlog():
    if request.method == "POST":
       if  "username" in session:
        email = request.values.get("email")
        title = request.values.get("title")
        content = request.values.get("content")
        user_id = session['user_id']
        blogRec = Posts(user_id=user_id, title=title, content=content, email=email)
        db.session.add(blogRec)
        db.session.commit()
        blogs = Posts.query.all()
        form=PostForm()
        return render_template("About.html", blogs=blogs, form=form)
       else:
          return redirect(url_for('account'))
    else:
        return "GET blog"

@app.route("/account", methods=["GET", "POST"])
def account():
    error = None
    if (request.method == "POST" or request.method == "GET") :
        username = request.values.get("username")
        password = request.values.get("password")

        ### Debug
        if username is None:
            print("username: None")
        else:
            print("username: " + username)
        if password is None:
            print("password: None")
        else:
            print("password: " + password)

        if username is None:
            return render_template('Account.html')

        userRec = User.query.filter_by(username=username, password=password).first()

        if userRec != None:

            ### Debug
            print("userRec.email: " + userRec.email)
            print("userRec.id: " + str(userRec.id))

            session['username'] = request.form['username']
            session['user_id'] = userRec.id
            db.session.add(userRec)
            db.session.commit()

            ### Store user to current_user
            login_user(userRec)
            flash("Login Success!!" + username)

            return redirect(url_for('p'))
        else:
            print("record not found")
            flash("Invalid username/password: " + username + "/" + password)
            error = "Username / Passord: " + username + "/" + password + " not found!!"

    if 'username' in session:
        session.pop('username', None)
        return render_template('p.html')
    else:
        return render_template('Account.html')
    #     if session['username'] is None:
    #         return render_template('p.html')
    #     else: 
    #         return render_template('Account.html')
    # else:
    #     return render_template('Account.html')

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
        
        user_Rec = User.query.filter_by(username=username).first()
        userEmail_Rec =  User.query.filter_by(email=email).first()
        
        print(user_Rec)
        if user_Rec == None:
            if userEmail_Rec == None:
                if password == confirm_password:
                    new_user = User(username=username, password=confirm_password, email=email)
                    print(new_user)
                    db.session.add(new_user)
                    db.session.commit()
                    subject = 'Register'
                    body = 'Thank you for registration'
                    smtp.sendR(email, subject, body)
                    print("email is sent to: " + email)
                    flash(f"user created {username} !!")
                    return redirect(url_for('account'))
                else:
                    print("password is different")
                    flash('wrong password')
            else:
                print("email is already exist: " + email)
                flash(" this email  has been taken ")
                return redirect(url_for('register'))
        else:
            print("name is already exist: " + username)
            flash(" this username has been taken ")
            return redirect(url_for('register'))

                
    
    return render_template("Register.html")

@app.route('/forget',methods=["GET", "POST"])
def forget():
    return render_template("Forget.html")

@app.route('/resetPassword',methods=["GET", "POST"])
def resetPassword():
    email = request.values.get("email")
    username = request.values.get("username")
    user_Rec = User.query.filter_by(email = email, username= username).first()

    if user_Rec != None:
        r1 = math.floor(random.uniform(0, 9))
        r2 = math.floor(random.uniform(0, 9))
        r3 = math.floor(random.uniform(0, 9))
        r4 = math.floor(random.uniform(0, 9))
        r5 = math.floor(random.uniform(0, 9))
        r6 = math.floor(random.uniform(0, 9))
        password = str(r1)+str(r2)+str(r3)+str(r4)+str(r5)+str(r6)
        print(username, password, email)
        stmt = (
        update(User).
        where(User.username == username).
        values(password=password)
        )
        db.session.execute(stmt)
        db.session.commit()
        subject = 'Reset password'
        body = 'Your new password is '+ password
        smtp.sendR(email, subject, body)
        print("email is sent to: " + email)
        flash(f"password is sent {username} !!")
        return redirect(url_for('account'))
    else:
        flash(f"invalid username or email !!")
        return redirect(url_for('account'))



@app.route("/cart")
def cart():
    # if 'user_name' in session:
    #     userName = session['user_name']
    # else:
    print("/cart ...")
    if "username" not in session:
        flash("Please login")
        return redirect(url_for('account'))
    cartlist=[]
    totalPrice = 0
    quantity = 0
    unitPrice = 0
    if "cart" in session:
        for productitem in session["cart"]:
            cartitem = []
            for key, value in productitem.items():
                cartitem.append(value)
                if key == "quantity":
                    quantity = int(value)
                if key == "unitPrice":
                    unitPrice = int(value)
            subtotal = quantity * unitPrice
            totalPrice = totalPrice + subtotal
            cartitem.append(subtotal)
            # cartitem.append(productitem)
            cartlist.append(cartitem)
            
        return render_template("Cart.html", cartlist=cartlist, totalPrice=totalPrice)
        #return render_template('Cart.html')
    flash(f"Nothing in cart!!")
    return render_template("p.html")



@app.route('/cartdelete/<cartitem>',methods=["GET", "POST"])
def cartdelete(cartitem):
    # cartitem = request.args.get('cartitem')
    print("<<<<")
    print(cartitem)
    if "cart" in session:
        cartLenStr = ""
        rowIndex = 0
        # resultIndex = -1
        cartList = session["cart"]
        for productitem in cartList:
            for key, value in productitem.items():
                if key == "id":
                    cartLenStr = value
                    if cartitem.find(cartLenStr) >= 0:
                        # resultIndex = rowIndex
                        print (cartList)
                        removed_element = cartList.pop(rowIndex)  
                        print(removed_element)
                        print (cartList)
                        print(rowIndex)
                        if cartLenStr.find("adopt") >= 0:
                            print("<<<< adoptitem")
                            adoptitem_id = removed_element["product"]
                            # startPos = removed_element.find("'product': '")
                            # endPos = removed_element.find("', 'productTitle'")
                            # startPos = startPos + 12
                            # adoptitem_id = removed_element[startPos:endPos]
                            # print(removed_element)
                            # print(str(startPos))
                            # print(str(endPos))
                            print(adoptitem_id)
                            print(">>>> adoptitem")
                            stmt = (
                                update(Adopt).
                                where(Adopt.id == adoptitem_id).
                                values(adopted = False)
                            )
                            db.session.execute(stmt)
                            db.session.commit()
                        print(">>>>")
            rowIndex = rowIndex + 1
        session["cart"] = cartList
        # if resultIndex != -1:
        #     session["cart"].pop(resultIndex, None)
    print(session["cart"])
    print('displayorder')
    # session["cart"].remove(newMap)
    print('1')
    # return redirect(url_for('Cart.html'))
    return redirect(url_for('cart'))

# @app.route('/cartdelete/<cartitem>',methods=["GET", "POST"])
# def cartdelete(cartitem):
#     # cartitem = request.args.get('cartitem')
#     print("<<<<")
#     print(cartitem)
#     if "cart" in session:
#         cartLenStr = ""
#         rowIndex = 0
#         # resultIndex = -1
#         for productitem in session["cart"]:
#             for key, value in productitem.items():
#                 if key == "id":
#                     cartLenStr = value
#                     if cartitem.find(cartLenStr) >= 0:
#                         # resultIndex = rowIndex
#                         print (session["cart"])
#                         removed_element = session.pop(rowIndex, None)  
#                         print(removed_element)
#                         print (session["cart"])
#                         print(rowIndex)
#                         print(">>>>")
#             rowIndex = rowIndex + 1
#         # if resultIndex != -1:
#         #     session["cart"].pop(resultIndex, None)
#     print(session["cart"])
#     print('displayorder')
#     # session["cart"].remove(newMap)
#     print('1')
#     # return redirect(url_for('Cart.html'))
#     return redirect(url_for('cart'))


# @app.route('/cartdelete/<cartitem>',methods=["GET", "POST"])
# def cartdelete(id):
#     # cartitem = request.args.get('cartitem')
#     try:
#         session.modified = True
#         for key , item in session['cart'].items():
#             if int(key) == id:
#                 print("<<<<")
#                 print("=====")

#                 print("=====")
#                 print(session["cart"])
#                 print(">>>>")
#                 print('displayorder')
#                 # session["cart"].remove(newMap)
#                 print('1')
#                 # return redirect(url_for('Cart.html'))
#                 session['cart'].pop(key, None)
#                 return redirect(url_for('cart'))
#     except Exception as e:
#         print(e)
#         return redirect(url_for('cart'))




@app.route("/wanted",methods=["GET", "POST"])
def wanted():
    if (request.method == "POST" or request.method == "GET"):
        
        print(request.files)

        if  "username" in session:
            title = request.values.get("title")
            description = request.values.get("description")
            user_id = session['user_id']

            if request.files:
                pic = request.files['pic']
                if pic:
                    filename = secure_filename(pic.filename)
                    mimetype = pic.mimetype
                    lostRec = Lost(user_id=user_id, title=title, description=description, filename=filename, img=pic.read(), mimetype=mimetype)

                    db.session.add(lostRec)
                    db.session.commit()

            losts = Lost.query.all()
            lostlist = []
            for lostitem in losts:
                lostArray = []
                lostArray.append(lostitem.user_id)
                lostArray.append(lostitem.title)
                lostArray.append(lostitem.description)
                lostArray.append(lostitem.filename)
                data=BytesIO(lostitem.img)
                encode_img=base64.b64encode(data.getvalue())
                decode_img=encode_img.decode("UTF-8")
                lostArray.append(decode_img)
                lostArray.append(lostitem.mimetype)                
                lostlist.append(lostArray)
                print(lostitem.user_id)
            

            form=LostForm()
            return render_template("Wanted.html", form=form, losts=losts, lostlist=lostlist)
        else:
            return redirect(url_for('account'))
    else:
        return render_template("Wanted.html")
        #return "GET wanted"


if __name__ == '__main__':
    app.run(debug=True, port=8000)


