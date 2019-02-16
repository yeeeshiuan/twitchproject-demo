from project import db
from project.api.models import UserSSO


def add_usersso(username, email, picture, twitch_id=""):
    user = UserSSO(username=username,
                   email=email,
                   picture=picture,
                   twitch_id=twitch_id)
    db.session.add(user)
    db.session.commit()
    return user
