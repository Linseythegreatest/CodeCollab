from flask import Flask, render_template, request, session, redirect
import socketio

# Initialize Flask app and Socket.IO server
app = Flask(__name__)
sio = socketio.Server(async_mode='threading')
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# Global variables to store collaborative code
code = ''
users = set()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect('/login')
    return render_template('index.html', username=session['username'], code=code)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        users.add(session['username'])
        return redirect('/')
    return render_template('login.html')

@sio.on('connect')
def connect(sid, environ):
    if 'username' in session:
        sio.emit('user_connected', session['username'])

@sio.on('disconnect')
def disconnect(sid):
    if 'username' in session:
        users.remove(session['username'])
        sio.emit('user_disconnected', session['username'])

@sio.on('code_update')
def code_update(sid, data):
    global code
    code = data['code']
    sio.emit('code_update', code)

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)
