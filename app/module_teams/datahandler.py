from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from database import db


class Team(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.VARCHAR(100), nullable=False)
  nameShort = db.Column(db.VARCHAR(30), nullable=False)
  contact = db.Column(db.VARCHAR(100), nullable=True)
  phoneNumber = db.Column(db.VARCHAR(100), nullable=True)
  state = db.Column(db.Integer, server_default= "0")
  created_at = db.Column(db.DateTime(timezone=True),
                          server_default=func.now())

  def __repr__(self):
    return f'<Team {self.name}>'
  
  def getDict(self):
    return {
      'id' : self.id,
      'name' : self.name,
      'nameShort' : self.nameShort,
      'contact' : self.contact,
      'phone' : self.phoneNumber,
      'state' : self.state,
      'created_at' : self.created_at,

    }

def init():  
  try:
    print("initTeamDB")

  except Exception as e:
    print(e)

  try:
    return 0

#  except Error as e:
#    print(e)
#    return -2

  except Exception as e:
    print(e)
    return -1

#  finally:
#    if con:
#     con.close()





def addTeam(_data : dict):
  try:
    try:
      query = db.session.query(Team).order_by(Team.id.desc()).first()
      id = query.id + 1
    except:
      id = 0



    newTeam = Team(
      id = id,
      name = _data["name"],
      nameShort = _data.get("nameShort",None),
      contact = _data.get("contact",None),
      phoneNumber = _data.get("phoneNumber", None),
      state = 1
    )
    print(newTeam)
    db.session.add(newTeam)
    db.session.commit()
    return 0

#  except Error as e:
#    print(e)
#    return -2

  except Exception as e:
    print(e)
    return -1

#  finally:
#    if con:
#      con.close()


def getTeams():
  try:
    query = db.session.query(Team)
    return query.all()

#  except Error as e:
#    print(e)
#    return -2

  except Exception as e:
    print(e)
    return -1

#  finally:
#    if con:
#      con.close()
