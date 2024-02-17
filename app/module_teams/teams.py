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


@teams_Blueprint.route('/deleteTeam', methods=['POST'])
def deleteTeam():
    if request.method == 'POST':
        try:
            data = request.json
            id=data.get("id")
            team = Team.query.get(id)
            db.session.delete(team)
            db.session.commit()
            return {'delteded' : id}
        except Exception as e:
            return {'error': e}

    else:
        return {'error': 0}

@teams_Blueprint.route('/updateTeam', methods=['POST', 'GET'])
def updateTeam():
    if session.get('permission', 0) >= 2:
        if request.method == 'POST':
            form = request.form
            id = int(form.get("id",0))
            try:
                if id != 0:
                    team = Team.query.filter_by(id=id).first()
                    team.name = form.get("name_long","")
                    team.nameShort = form.get("name_short","")
                    team.contact = form.get("contact","")
                    team.phoneNumber = form.get("phone", "")
                    team.state = form.get("state", "")

                    db.session.commit()
                else:
                    newTeam = Team(
                        name = form["name_long"],
                        nameShort = form.get("name_short",None),
                        contact = form.get("contact",None),
                        phoneNumber = form.get("phone", None),
                        state = form.get("state", 1)
                        )
                    db.session.add(newTeam)
                    db.session.commit()
                
                return redirect(url_for('teams.overview'))


            except Exception as e:
                print(e)
                flash("Error updating team " + form["name_long"] )
            return redirect(url_for('teams.overview'))
            
        elif request.method == 'GET':
            return redirect(url_for('teams.overview'))
    else:
        return redirect(url_for('index'))


@teams_Blueprint.route('/getTeams', methods=['GET'])
def getTeams():    
    if session.get('permission', 0) >= 1:

        teams = db.session.query(Team)
        data = {}
        for team in teams:
            data[team.id] = {
                "id" : team.id,
                "name" : team.name,
                "nameShort" : team.nameShort,
                "contact" : team.contact,
                "state" : team.state,
                "phone" : team.phoneNumber,
                "created_at" : team.created_at,
            }
        return jsonify(data)
    else:
        return None
    

def getTeamById(id):
    try:
        query = db.session.query(Team).where(Team.id == id)[0]
        return query.getDict()
    except Exception as e:
        print(e)
        return {"error":-3}   