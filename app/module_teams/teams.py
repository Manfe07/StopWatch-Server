from flask import Blueprint, render_template, Flask, request, jsonify, redirect, url_for, session, flash
import module_teams.datahandler as datahandler

teams_Blueprint = Blueprint('teams', __name__,  template_folder='templates')

def init():
    datahandler.init()

@teams_Blueprint.route('/', methods=['GET'])
def overview():
    teams = datahandler.getTeams()
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
        teamData = {
            'name' : form['name'],
            'info1' : form['info1'],
            'info2' : form['info2'],
            'url' : form['url'],
        }
        if datahandler.addteam(teamData):
            return redirect(url_for('teams.overview'))
        else:
            flash("Error creating team " + teamData["name"] )
            return redirect(url_for('teams.overview'))
    elif request.method == 'GET':
        return redirect(url_for('teams.overview'))


def getteamById(id):
    try:
        query = datahandler.db.session.query(datahandler.team).where(datahandler.team.id == id)[0]
        return query.getDict()
    except Exception as e:
        print(e)
        return {"error":-3}   