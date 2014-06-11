# -*- coding: utf-8 -*-
from flask import Flask,request, session, g, redirect, url_for, abort
from flask import render_template, flash
import os,sqlite3
import time
from werkzeug import check_password_hash, generate_password_hash
from contextlib import closing

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'flask.db'),
	DEBUG=True,
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='default'
))
app.config.from_envvar('flask_setting',silent=True)

def connect_db():
	rv = sqlite3.connect(app.config['DATABASE'])
	return rv

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

def query_db(query, args=(), one=False):
	"""퀴리 날리고 결과 리턴"""
	cur = g.db.execute(query, args)
	rv = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]

	return (rv[0] if rv else None) if one else rv

def get_user_id(username):
	"""유저이름을 인자로 받고 해당 id 리턴"""
	rv = g.db.execute('select id from user where username =?', [username]).fetchone()

	return rv[0] if rv else None

def format_datetime(timestamp):
	"""타임스탬프"""
	return datatime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

@app.before_request
def before_request():
	"""디비에 요청하기 전에 확인을 위한 함수"""
	g.db = connect_db()
	g.user = None
	if 'id' in session:
		g.user = query_db('select * from user where id = ?', [session['id']], one=True)
		
@app.teardown_request
def teardown_request(exception):
	"""디비 닫음"""
	if hasattr(g, 'db'):
		g.db.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
	"""신규 가입"""
	if g.user:
		return redict(url_for('main'))
	error = None
	if request.method == 'POST':
		"""입력값 검사, 아이디에 대해선 수정 필요"""
		if not request.form['username']:
			error = '아이디를 입력하세요.'
		elif not request.form['password']:
			error = '비밀번호를 입력하세요.'
		elif request.form['password'] != request.form['password2']:
			error = '입력하신 두 비밀번호가 다릅니다.'
		elif get_user_id(request.form['username']) is not None:
			error = '사용할 수 없는 아이디 입니다.'
		else:
			g.db.execute('''insert into user (username, password) values (?,?)''', [request.form['username'],generate_password_hash(request.form['password'])])
			g.db.commit()
			flash('성공적으로 가입되었습니다.')
			return redirect(url_for('main'))
	return render_template('register.html', error=error)



"""메인 화면"""
@app.route('/')
def main():
    return render_template('main.html')

"""로그인 로그아웃"""
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		user = query_db('''select * from user where username = ?''',[request.form['username']], one=True)
		if user is None:
			error = '그런 아이디는 존재하지 않습니다.'
		elif not check_password_hash(user['password'], request.form['username']):
			error = '비밀 번호가 잘못되었습니다.'
		else:
			flash('로그인 성공')
			session['id'] = user['id']
			return redirect(url_for('main'))
	return render_template('main.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_user'))


if __name__ == '__main__':
    app.run()
