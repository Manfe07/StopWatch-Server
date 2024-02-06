from flask import Blueprint, render_template, Flask, request, jsonify, redirect, url_for, session, flash
import module_teams.datahandler as dh
from module_teams.datahandler import db, Team


teams_Blueprint = Blueprint('teams', __name__,  template_folder='templates')

def init():
    dh.init()

@teams_Blueprint.route('/', methods=['GET'])
def overview():
    teams = dh.getTeams()
    #teams = datahandler.db.session.query(datahandler.Team)
    #result = {}
    #for r in query:
    #   result[r.id] = r.getDict()
    return render_template('teams/manageTeams.html', teams=teams)


@teams_Blueprint.route('/addteam', methods=['POST', 'GET'])
def addteam():
    if request.method == 'POST':
        form = request.form
        #ToDo: change to new format
 
        try:
            newTeam = Team(
            name = form["name_long"],
            nameShort = form.get("name_short",None),
            contact = form.get("contact",None),
            phoneNumber = form.get("phone", None),
            state = form.get("state", 1)
            )
            print(newTeam)
            db.session.add(newTeam)
            db.session.commit()

            return redirect(url_for('teams.overview'))


        except Exception as e:
            print(e)
            flash("Error creating team " + form["name_long"] )
            return redirect(url_for('teams.overview'))
        
    elif request.method == 'GET':
        return redirect(url_for('teams.overview'))


def getTeamById(id):
    try:
        query = db.session.query(Team).where(Team.id == id)[0]
        return query.getDict()
    except Exception as e:
        print(e)
        return {"error":-3}   