from flask import Blueprint, render_template, Flask, request, jsonify, redirect, url_for, session, flash
import module_teams.datahandler as dh
from module_sales.models import db, Item, ItemGroup
from module_users.datahandler import User
from module_users.users import getSessionUser


sales_Blueprint = Blueprint('sales', __name__, template_folder='templates')

def init():
    return True

@sales_Blueprint.route('/', methods=['GET'])
def overview():
    if session.get('permission', 0) >= 1:
        itemGroups = db.session.query(ItemGroup)
        items = db.session.query(Item)
        users = {}
        for user in db.session.query(User):
            users[user.id] = user

        return render_template('sales/overview.html', itemGroups=itemGroups, items=items, users=users)
    else:
        return redirect(url_for('index'))

@sales_Blueprint.route('/addItemGroup', methods=['GET','POST'])
def addItemGroup():
    if session.get('permission', 0) >= 2:
        if request.method == 'POST':
            form = request.form
            try:
                newItemGroup = ItemGroup(
                    name = form["name"],
                    description = form.get("description",None),
                    color = form.get("color",None),
                    state = form.get("state", 0)
                )
                print(newItemGroup)
                db.session.add(newItemGroup)
                db.session.commit()

                return redirect(url_for('sales.overview'))


            except Exception as e:
                print(e)
                flash("Error creating itemGroup " + form["name"] )
            return redirect(url_for('sales.overview'))
            
        elif request.method == 'GET':
            return redirect(url_for('sales.overview'))
    else:
        return redirect(url_for('index'))


@sales_Blueprint.route('/updateItemGroup', methods=['GET','POST'])
def updateItemGroup():
    if session.get('permission', 0) >= 2:
        if request.method == 'POST':
            form = request.form
            try:
                group = ItemGroup.query.filter_by(id=form.get("id")).first()
                
                group.name = form.get("name",group.name)
                group.descripton = form.get("description",group.description)
                group.color = form.get("color",group.color)
                group.state = form.get("state",group.state)
                db.session.commit()

                return redirect(url_for('sales.overview'))


            except Exception as e:
                print(e)
                flash("Error updating itemGroup " + form["name"] )
            return redirect(url_for('sales.overview'))
            
        elif request.method == 'GET':
            return redirect(url_for('sales.overview'))
    else:
        return redirect(url_for('index'))


@sales_Blueprint.route('/addItem', methods=['GET','POST'])
def addItem():
    if session.get('permission', 0) >= 2:
        if request.method == 'POST':
            form = request.form
            newItem = Item(
                name = form.get("name"),
                description = form.get("description",None),
                price = form.get("price",0.0),
                state = form.get("state", 0),
                groupId = form.get("groupId",0),
                changedBy = session.get('user_id', None)
            )
            print(newItem)
            db.session.add(newItem)
            db.session.commit()

            return redirect(url_for('sales.overview'))

        elif request.method == 'GET':
            return redirect(url_for('sales.overview'))
    else:
        return redirect(url_for('index'))


@sales_Blueprint.route('/getGroups', methods=['GET'])
def getGroups():    
    if session.get('permission', 0) >= 1:

        itemGroups = db.session.query(ItemGroup)

        groupData = {}
        for group in itemGroups:
            itemData = []
            for item in group.items:
                itemData.append(
                    {
                        "id" : item.id,
                        "name" : item.name,
                        "description" : item.description,
                        "price" : item.price,
                        "state" : item.state,
                        "changedBy" : item.changedBy,
                    }
            )
            groupData[group.id] = {
                "id" : group.id,
                "name" : group.name,
                "description" : group.description,
                "color" : group.color,
                "state" : group.state,
                "items" : itemData,
            }

        return jsonify(groupData)
    else:
        return None

@sales_Blueprint.route('/getItems', methods=['GET'])
def getItems():    
    if session.get('permission', 0) >= 1:

        items = db.session.query(Item)

        data = {}
        for item in items:
            data[item.id] = {
                "id" : item.id,
                "name" : item.name,
                "description" : item.description,
                "price" : item.price,
                "state" : item.state,
                "changedBy" : item.changedBy,
            }
        return jsonify(data)
    else:
        return None

@sales_Blueprint.route('/cashRegister', methods=['GET'])
def cashRegister():
    if session.get('permission', 0) >= 1:
    
        itemGroups = db.session.query(ItemGroup)

        return render_template('sales/cashRegister.html', itemGroups=itemGroups)
    else:
        return redirect(url_for('index'))

