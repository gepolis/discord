from peewee import *
from pathlib import Path

path = Path(__file__).parent.parent.resolve()
db_path = path / "db/mafia.db"

db = SqliteDatabase(db_path)


class MafiaRoomMembers(Model):
    user_id = IntegerField()
    role = CharField()

    class Meta:
        database = db


class MafiaRooms(Model):

    category_id = IntegerField(null=True)
    owner_id = IntegerField()
    max_players = IntegerField()
    mafia_count = IntegerField()
    invite = CharField()
    leading_id = IntegerField(null=True)
    control_channel = IntegerField()
    vote_channel = IntegerField()
    room_channel = IntegerField()
    owner_channel = IntegerField()
    end = BooleanField(default=False)
    start = BooleanField(default=False)
    members = ManyToManyField(MafiaRoomMembers, backref="room")



    class Meta:
        database = db


db.create_tables([MafiaRooms, MafiaRoomMembers])