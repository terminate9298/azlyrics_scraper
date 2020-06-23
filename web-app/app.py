from flask import Flask , request , jsonify , render_template , redirect , url_for
# from bin.main import Get_Lyrics
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)

ENV = 'prod' 
if ENV == 'dev':
	app.debug = True
	app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:kaus98@localhost/lyrics'
	
else:
	app.config['SQLALCHEMY_DATABASE_URI'] =  'URI HERE'
	app.debug = False 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Lyrics_dataset(db.Model):
	__tablename__ =  'lyrics_dataset'
	id = db.Column(db.Integer , primary_key = True)
	song_name = db.Column(db.String(200))
	singer = db.Column(db.String(200))
	url = db.Column(db.String(200), unique = True)
	call = db.Column(db.String(200))
	lyrics = db.Column(db.Text())

	def __init__(self , song_name ,  singer , url , call , lyrics):
		self.song_name = song_name
		self.singer = singer
		self.url = url
		self.call = call
		self.lyrics = lyrics
	
	def serialize(self):
		return {
		'id' : self.id ,
		'song_name' : self.song_name,
		'singer' : self.singer,
		'url' : self.url,
		'call' : self.call,
		'lyrics' : self.lyrics
				}
	def short_serialize(self):
		return {
		'id' : self.id ,
		'song_name' : self.song_name,
		'singer' : self.singer,
		'url' : self.url,
		'call' : self.call
				}

def serialize(data):
	return [{'id': dt[0] , 'song_name':dt[1] , 'singer':dt[2] , 'url': dt[3] ,'call':dt[4] , 'lyrics': dt[5]} for dt in data]

def short_serialize(data):
	return [{'id': dt[0] , 'song_name':dt[1] , 'singer':dt[2] , 'url': dt[3] ,'call':dt[4] } for dt in data]

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/form/get/' , methods = ['GET'])
def form_search():
	data = request.args.get('search')
	if request.args.get('search_in')=='lyrics':
		return redirect(url_for('search' , search = data))
	else:
		return redirect(url_for('lyrics' , song_name = data))

@app.route('/lyrics/call/<song_name>')
def lyrics(song_name):
	data = db.session.execute("SELECT * from Lyrics_dataset where LOWER(song_name) like '%{}%' ".format(song_name.lower()))
	return render_template('main.html' , data = short_serialize(data))

@app.route('/lyrics/id/<song_id>')
def id(song_id):
	data = Lyrics_dataset.query.filter_by(id = song_id).all()
	return render_template('lyrics.html' , data = [dt.serialize() for dt in data])

@app.route('/lyrics/singer/<singer_name>')
def singer(singer_name):
	data = Lyrics_dataset.query.filter_by(singer = singer_name).all()
	return render_template('singer.html' , data = [dt.short_serialize() for dt in data])

@app.route('/lyrics/search/<search>')
def search(search):
	data = db.session.execute("SELECT * from Lyrics_dataset where LOWER(lyrics) like '%{}%' ".format(search.lower()))
	return render_template('search.html' , data = short_serialize(data))


@app.route('/api/lyrics/call/<song_name>')
def api_lyrics(song_name):
	data = db.session.execute("SELECT * from Lyrics_dataset where LOWER(song_name) like '%{}%' ".format(song_name.lower()))
	
	return jsonify(serialize(data))

@app.route('/api/lyrics/id/<song_id>')
def api_id(song_id):
	data = Lyrics_dataset.query.filter_by(id =song_id).all()
	return jsonify([dt.serialize() for dt in data])

@app.route('/api/lyrics/singer/<singer_name>')
def api_singer(singer_name):
	data = Lyrics_dataset.query.filter_by(singer = singer_name).all()
	return jsonify([dt.serialize() for dt in data])

@app.route('/api/lyrics/search/<search>')
def api_search(search):
	if len(name) > 5:
		data = db.session.execute("SELECT * from Lyrics_dataset where LOWER(lyrics) like '%{}%' ".format(search.lower()))
	# print(data)
	# for df in data:
	# 	print(df[1])
		return jsonify(serialize(data))
	else:
		return jsonify({'error':'Send Bigger string'})


if __name__ == '__main__':
	app.run(debug = True)