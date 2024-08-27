from flask import Flask ,jsonify, render_template, request,make_response ,session
from  database import dbinitialization
from database.models import User
from database.models import Restaurant
from database.models import Order
from database.models import MenuItem
from flask_restful import Api

from resource import routes
from datetime import datetime
app = Flask(__name__)
app.config["MONGODB_SETTINGS"]={'host':"mongodb://localhost:27017/FoodExpress"}
dbinitialization.initialize_db(app)
app = Flask(__name__)
app.secret_key="bsjvhusdhg5565645"
api=Api(app)
routes.initialize_routes(api)
@app.route("/")
def loginform():
    return render_template("Login.html")

@app.route("/login",methods=["POST"])
def login():
    try:
        uname=request.form["uname"]
        pwd = request.form["pwd"]
        data =User.objects(userName=uname)
        if data:
            session["uname"]=uname
            mydata = User.objects()
            utype = ""
            for i in range(len(mydata)):
                if uname == mydata[i]["userName"]:
                    utype = mydata[i]["userType"]
                    session["utype"] = utype
                    break
            if utype == "Buyer":
                return render_template("home.html", name=uname)
            elif utype == "Restaurant Owner":
                return render_template("Owner.html", name=uname)
            else:
                status = Order.objects(orderStatus="False")
                if status:
                    return render_template("rider.html", data=status, name=uname)
                else:
                    return render_template("wait.html", name=uname)

        else:
            return render_template("Login.html", error="login failed, First Sign In To System")
    except Exception as e:
        return render_template("Login.html",error="Login error"+str(e))

@app.route("/logout")
def logout():
    try:
        session.clear()
        return render_template("login.html")
    except Exception as e:
        return render_template("Login.html", error=str(e))

@app.route("/signupform")
def signupform():
    return render_template("Login.html")


@app.route("/signup",methods=["POST"])
def signup():
    try:
        uname=request.form["uname"]
        pwd = request.form["pwd"]
        conpwd = request.form["conpwd"]
        email = request.form["email"]
        utype= request.form["utype"]
        if email == "" or uname == "" or pwd == "" or utype == "" or conpwd == "":
            return render_template("signup.html", error="Please Enter  all required details")
        if pwd != conpwd:
            return render_template("signup.html", error="Password and confirm password should be same")
        login=User.objects(userName=uname)
        if login:
            return render_template("signup.html", error="This user already exist")
        else:
            session["uname"]=uname
            session["utype"]= utype
            t = User(userName=uname,password=pwd,email =email,userType=utype).save()
            if utype == "Buyer":
                return render_template("diet.html", name =uname)
            elif utype == "Restaurant Owner":
                return render_template("Owner.html", name = uname)
            else:
                status = Order.objects(orderStatus="False")
                if status:
                    return render_template("rider.html", data=status, name=uname)
                else:
                    return render_template("wait.html", name=uname)

    except Exception as e:
        return render_template("login.html",error="sign up error"+str(e))


@app.route("/addMenuesForm")
def addMenuesForm():
    uname = session.get("uname")
    utype = session.get("utype")
    if uname != None and utype == "Restaurant Owner":
        return render_template("AddMenues.html")
    else:
        return render_template("Login.html", error = "First Login to system with Owner Credientials")

@app.route("/addmenues", methods = ['GET', 'POST'])
def addmenues():
    try:
        oname = session.get("uname")
        rname = request.form["rname"]
        data = Restaurant.objects(ownerName=oname)
        if data:
            return render_template("Owner.html", name = oname, error="Please add your Items from Update Menues")
        else:
            menu_items = []
            for i in range(1, 3 + 1):
                item_name = request.form.get(f'item_name_{i}')
                price = float(request.form.get(f'price_{i}'))
                quantity = int(request.form.get(f'quantity_{i}'))
                menu_item = MenuItem(itemName=item_name, price=price, quantity=quantity)
                menu_items.append(menu_item)
            spec = request.form["spec"]
            contact = request.form["contact"]
            address = request.form["adrs"]
            Restaurant(ownerName=oname, name=rname, menu=menu_items, speciality=spec, contact=contact,
                       address=address).save()
            return render_template("Owner.html", name=oname)
    except Exception as e:
        return render_template("AddMenues.html", error = str(e))

@app.route("/updateMenueForm")
def updateMenueForm():
    uname = session.get("uname")
    utype = session.get("utype")
    if uname != None and utype == "Restaurant Owner":
        return render_template("UpdateMenues.html")
    else:
        return render_template("Login.html", error = "First Login to system with Owner Credientials")

@app.route("/updateMenue", methods=['GET', 'POST'])
def updateMenue():
    try:
        oname = session.get("uname")
        rname = request.form["rname"]
        data = Restaurant.objects(ownerName=oname)

        if rname == data[0]["name"]:
            action = request.form["action"]
            noOfItems = request.form["no"]
            menu_items = []

            for i in range(1, int(noOfItems) + 1):
                item_name = request.form.get(f'item_name_{i}')
                price = float(request.form.get(f'price_{i}'))
                quantity = int(request.form.get(f'quantity_{i}'))
                menu_item = MenuItem(itemName=item_name, price=price, quantity=quantity)
                menu_items.append(menu_item)

            spec = request.form["spec"]
            contact = request.form["contact"]

            if spec != '':
                Restaurant.objects(ownerName=oname).update(speciality=spec)

            if contact != '':
                Restaurant.objects(ownerName=oname).update(contact=contact)

            existing_menu_items = Restaurant.objects(ownerName=oname).first().menu

            if action == "Update":
                for item in menu_items:
                    existing_item = next((i for i in existing_menu_items if i.itemName == item.itemName), None)
                    if existing_item:
                        existing_item.price = item.price
                        existing_item.quantity = item.quantity

            elif action == "Add":
                restaurant = Restaurant.objects(ownerName=oname)
                j = 0
                for i in restaurant:
                    # print(i["menu"][j]["itemName"])
                    for j in i["menu"]:
                        item = MenuItem(itemName=j["itemName"], price=j["price"], quantity=j["quantity"])
                        menu_items.append(item)
                Restaurant.objects(ownerName=oname).update(menu=menu_items)
            return render_template("Owner.html", name=oname)
        else:
            return render_template("Owner.html", error="This Restaurant does not exist in the Database")

    except Exception as e:
        return render_template("UpdateMenues.html", error=str(e))

@app.route("/showmenues")
def showmenues():
    try:
        utype = session.get("utype")
        uname = session.get("uname")
        if utype == "Restaurant Owner":
            data = Restaurant.objects(ownerName=uname)
            return render_template("ShowMenue.html", name=uname, data=data)

        else:
            return render_template("Login.html", error="Login with Owner Credientials")
    except Exception as e:
        return render_template("Owner.html", error=str(e))


@app.route("/dietform")
def dietform():
    name = session.get("uname")
    if name:
        return render_template("diet.html")
    else:
        return render_template("login.html", error="Please login first")


@app.route("/diet",methods=["POST"])
def diet():
    try:
        food=request.form["foodPreference"]
        print(food)
        dat =Restaurant.objects(speciality=food)
        return render_template("Restaurant.html",name=food,data=dat)

    except Exception as e:
        return render_template("login.html",error="diet error"+str(e))

@app.route("/restaurantform")
def restaurantform():
    name = session.get("uname")
    if name:
        return render_template("Restaurant.html")
    else:
        return render_template("login.html", error="Please login first")


@app.route("/restaurant",methods=["POST"])
def restaurant():
    try:
        choice=request.form["choice"]
        session['resname']=choice
        dat =Restaurant.objects(name=choice)
        return render_template("menu.html",name=choice,data=dat)

    except Exception as e:
        return render_template("login.html",error="restaurant error"+str(e))

@app.route("/Allrestaurant")
def Allrestaurant():
    name = session.get("uname")
    if name:
        return render_template("AllRestaurants.html")
    else:
        return render_template("login.html", error="Please login first")

@app.route("/riderform")
def riderform():
    name = session.get("uname")
    if name:
        return render_template("rider.html")

    else:
        return render_template("login.html", error = "Please login first")



@app.route("/rider",methods=["POST"])
def rider():
    try:
        food=request.form["date"]
        datetime = request.form["datetime"]
        status = "True"
        dic={"deliveryTime":datetime,"orderStatus":"True"}
        print(datetime)
        data = Order.objects(name=food)
        print(data)
        if data:
            print('hello2')
            print(food)
            print(datetime)
            Order.objects(name=food).update(deliveryTime=datetime, orderStatus=status)
            dat = Order.objects(name=food)
            return render_template("status.html", data=dat)
        else:
            dicc = {"orderStatus": "False"}
            name = session.get("uname")
            print('hello')
            sta = Order.objects(**dicc)
            return render_template("rider.html", name=name, data=sta, message="Please enter correct name")
    except Exception as e:
        return render_template("login.html",error="rider error"+str(e))



@app.route('/orderform')
def orderform():
    uname = session.get("uname")
    if uname:
        return render_template("order.html")
    else:
        return render_template('login.html', error="Login Error")

@app.route('/order', methods=["POST"])
def order():
    try:
        uname = session.get("uname")
        if uname:
            uname = session.get('uname')
            itemname = request.form['itemname']
            quantity = request.form['quantity']
            quantity = int(quantity)
            totalprice = 0.0
            RestaurantName = session.get('resname')

            a = []
            orig = []
            res = Restaurant.objects(name=RestaurantName).first()
            print(res)
            for j in res.menu:
                if j.itemName == itemname:
                    price = j.price
                    orig_quantity = j.quantity
                    j.quantity = quantity
                    menu_items = j
                    # new code:
                    if orig_quantity >= quantity and orig_quantity > 0:
                        orig_quantity = orig_quantity - quantity
                        orig.append({'itemname': itemname , 'orig_quantity': orig_quantity})
                        session['orig'] = orig
                    else:
                        return render_template('order.html' , error = 'This much quantity isnt availible!')
                    a.append(j)

            session['add'] = a

            quantity = int(quantity)
            totalprice = totalprice + (price * quantity)
            disc = (totalprice / 100) * 5  # 5 percent
            ml = []
            ml.append(menu_items)
            session['menuitems'] = ml
            session["totalprice"] = totalprice

            ord = Order(
                uname=uname, items=ml, totalPrice=totalprice, discount=disc, orderStatus="False",
                address="Abcd block Lahore",
                deliveryTime=None
            ).save()

            id = str(ord.id)
            session['id'] = id
            return render_template('addtocart.html')

        else:
            return render_template('login.html', error="Login Error")

    except Exception as e:
        return render_template('login.html', error=str(e))



@app.route('/addtocartform')
def addtocartform():
    uname = session.get("uname")
    if uname:
        return render_template('addtocart.html')
    else:
        return render_template('login.html', error="Login Error")


@app.route('/addremoveitems')
def addremoveitems():
    uname = session.get("uname")
    if uname:
        return render_template('addremoveitems.html')
    else:
        return render_template('login.html', error="Login Error")


@app.route('/addtocart' , methods = ["POST"])
def addtocart():
    try:
        uname = session.get("uname")
        if uname:
            RestaurantName = session.get('resname')
            itemname = request.form['itemname']
            action = request.form['action']
            quantity = request.form['quantity']
            quantity = int(quantity)
            addit = session.get("add")
            if action == 'add':
                res = Restaurant.objects(name=RestaurantName).first()
                found = False
                if res:
                    for j in res.menu:
                        if j.itemName == itemname:
                            orig_quantity = j.quantity
                            j.quantity = quantity
                            orig = session.get('orig')

                            for i in orig:
                                if i['itemname'] == itemname:
                                    orig_quantity = i['orig_quantity']
                                    if orig_quantity >= quantity and orig_quantity > 0:
                                        orig_quantity = orig_quantity - quantity
                                        i['orig_quantity'] = orig_quantity
                                        session['orig'] = orig
                                        found = True
                                    else:
                                        return render_template('addremoveitems.html',
                                                               error='This much quantity isnt availible!')

                            if found == False:
                                if orig_quantity >= quantity and orig_quantity > 0:
                                    orig_quantity = orig_quantity - quantity
                                    orig.append({'itemname': itemname , 'orig_quantity' : orig_quantity})
                                    session['orig'] = orig
                                else:
                                    return render_template('addremoveitems.html',
                                                           error='This much quantity isnt availible!')

                            addit.append(j)
                session["add"] = addit
                return render_template('addtocart.html')
            elif action == 'remove':
                #remove items from the add list
                for i in addit:  # remove items
                    if i["itemName"] == itemname:
                        addit.remove(i)

                session["add"] = addit
                return render_template('addtocart.html')
        else:
            return render_template('login.html', error= "Login Error")
    except Exception as e:
        return render_template('login.html', error=str(e))



@app.route('/confirmorder' , methods= ["GET" , "PUT"])
def confirmorder():
    try:
        uname = session.get("uname")
        if uname:
            Totalprice = 0.0
            addit = session.get("add")

            #  Get prices and the quantities of items to be added

            for i in addit:
                Totalprice = Totalprice + (i["price"] * i["quantity"] )

            session["totalprice"] = Totalprice
            disc = (Totalprice / 100) * 5  # 5 percent
            session["disc"] = disc
            id = session.get('id')
            dic = {"items": addit, "totalPrice": Totalprice, "discount": disc }

            Order.objects(id=id).update(**dic)
            totalincome = 0.0
            RestaurantName = session.get("resname")
            res = Restaurant.objects(name=RestaurantName).first()
            if res:
                totalincome = res.TotalIncome
                totalincome = totalincome + Totalprice
                res.TotalIncome = totalincome
                menu = res.menu
                #Change the quantities in MenuItem in restaurant
                for i in menu:
                    for j in addit:
                        if i["itemName"] == j["itemName"]:
                            q = j["quantity"]
                            newquantity = i["quantity"]
                            newquantity = newquantity - q
                            i["quantity"] = newquantity
                res.menu = menu

            res.save()

            ord = Order.objects(id=id).first()

            session['ord'] = ord.items
            return render_template('addtocart.html')
        else:
            return render_template('login.html', error= "Login Error")
    except Exception as e:
        return render_template('login.html', error=str(e))

@app.route('/bill')
def bill():
        try:
            uname = session.get("uname")
            if uname:
                return render_template('Bill.html')
        except Exception as e:
            return render_template('login.html', error=str(e))

@app.route('/getBill' , methods=["GET"])
def getbill():
    try:
        uname = session.get("uname")
        if uname:
            disc = session.get('disc')
            ord = session.get('ord')
            RestaurantName = session.get("resname")
            totalprice = session.get('totalprice')
            restaurant_obj = Restaurant.objects(name=RestaurantName).first()
            # Check if the restaurant exists
            if restaurant_obj:
                totalincome = restaurant_obj.TotalIncome

                totalincome = totalincome - disc
                restaurant_obj.TotalIncome = totalincome

            restaurant_obj.save()

            return jsonify({'disc': disc, 'ord': ord, 'totalprice': totalprice})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/checkdetails', methods=["GET"])
def checkdetails():
    try:
        uname = session.get("uname")
        if uname:
            # Get the name of the restaurant owner (username)
            name = session.get("uname")

            # Get the restaurant information based on the owner's name
            res = Restaurant.objects(ownerName=name).first()

            if res:
                earning = res.TotalIncome

                # Fetch all orders from the database with the restaurant's name
                orders = Order.objects(items_itemName_in=[item.itemName for item in res.menu])

                # Prepare a dictionary to hold user information and their ordered items
                user_orders_info = {}

                for order in orders:
                    user_name = order.uname
                    user_orders = []

                    # Find the items from the order that belong to the current restaurant
                    for item in order.items:
                        if item.itemName in [menu_item.itemName for menu_item in res.menu]:
                            user_orders.append(item)

                    user_orders_info[user_name] = user_orders

                return render_template('checkdetails.html',earning = earning, user_orders_info=user_orders_info, name=name, resname=res.name)

            else:
                return render_template('checkdetails.html', error="No restaurant found for this owner.", name=name)

        else:
            return render_template('login.html', error="Login Error")
    except Exception as e:
        return render_template('login.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True, port=8001)
