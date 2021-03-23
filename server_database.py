from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker

from common.variables import SERVER_DATABASE


class ServerStorage:
    class AllUsers:
        def __init__(self, username):
            self.username = username
            self.last_login = datetime.now()
            self.id = None

    class ActiveUsers:
        def __init__(self, user_id, ip_adress, port, login_time):
            self.user_id = user_id
            self.ip_adress = ip_adress
            self.port = port
            self.login_time = login_time
            self.id = None

    class LoginHistory:
        def __init__(self, user_id, date, ip_adress, port):
            self.user_id = user_id
            self.date = date
            self.ip_adress = ip_adress
            self.port = port
            self.id = None

    def __init__(self):
        self.database_engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200)

        self.metadata = MetaData()

        users_table = Table(
            'Users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('username', String, unique=True),
            Column('last_login', DateTime),
        )

        active_users_table = Table(
            'Active_users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', ForeignKey('Users.id'), unique=True),
            Column('ip_adress', String),
            Column('port', Integer),
            Column('login_time', DateTime),
        )

        login_history_table = Table(
            'Login_history', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', ForeignKey('Users.id')),
            Column('ip_adress', String),
            Column('port', Integer),
            Column('date', DateTime),
        )

        self.metadata.create_all(self.database_engine)

        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, login_history_table)

        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_adress, port):
        res = self.session.query(self.AllUsers).filter_by(username=username)

        if res.count():
            user = res.first()
            user.last_login = datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()

        new_active_user = self.ActiveUsers(user.id, ip_adress, port, datetime.now())
        self.session.add(new_active_user)

        history = self.LoginHistory(user.id, datetime.now(), ip_adress, port)
        self.session.add(history)

        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(username=username).first()

        self.session.query(self.ActiveUsers).filter_by(user_id=user.id).delete()

        self.session.commit()

    def users_list(self):
        query = self.session.query(
            self.AllUsers.username,
            self.AllUsers.last_login
        )

        return query.all()

    def active_users_list(self):
        query = self.session.query(
            self.AllUsers.username,
            self.ActiveUsers.ip_adress,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)

        return query.all()

    def login_history(self, username=None):
        query = self.session.query(
            self.AllUsers.username,
            self.LoginHistory.ip_adress,
            self.LoginHistory.port,
            self.LoginHistory.date
        ).join(self.AllUsers)

        if username:
            query = query.filter(self.AllUsers.username == username)

        return query.all()


if __name__ == '__main__':
    test_db = ServerStorage()
    test_db.user_login('user1', '192.168.0.1', 1234)
    test_db.user_login('user2', '192.168.0.2', 2345)
    print(test_db.users_list())
    print(test_db.active_users_list())

    test_db.user_logout('user1')
    print(test_db.active_users_list())

    print(test_db.login_history())
    print(test_db.login_history('user1'))
