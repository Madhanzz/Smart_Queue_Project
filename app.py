from flask import Flask, render_template, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_socketio import SocketIO, emit
import qrcode
import io
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///queue.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ------------------ Models ------------------
class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    status = db.Column(db.String(20), default="waiting")  # waiting / called / served
    called_at = db.Column(db.DateTime, nullable=True)

with app.app_context():
    db.create_all()

# ------------------ Routes ------------------
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/get_token')
def get_token():
    last_token = Token.query.order_by(Token.id.desc()).first()
    new_number = 1 if not last_token else last_token.number + 1
    token = Token(number=new_number)
    db.session.add(token)
    db.session.commit()
    return redirect(url_for('my_token', token_number=token.number))

@app.route('/my_token/<int:token_number>')
def my_token(token_number):
    token = Token.query.filter_by(number=token_number).first()
    if not token:
        return "Token not found", 404

    tokens_ahead = Token.query.filter(Token.status=="waiting", Token.id < token.id).count()
    avg_service_time = 5
    est_wait_time = tokens_ahead * avg_service_time

    return render_template(
        "my_token.html",
        token_number=token.number,
        status=token.status,
        tokens_ahead=tokens_ahead,
        est_wait_time=est_wait_time
    )

@app.route('/staff')
def staff_dashboard():
    return render_template("staff.html")

@app.route('/call_next')
def call_next():
    current_token = Token.query.filter_by(status="called").first()
    if current_token:
        current_token.status = "served"
        db.session.commit()
        socketio.emit('token_served', {'number': current_token.number})

    next_token = Token.query.filter_by(status="waiting").order_by(Token.id).first()
    if next_token:
        next_token.status = "called"
        next_token.called_at = datetime.now()
        db.session.commit()
        socketio.emit('token_called', {'number': next_token.number})

    return redirect(url_for('staff_dashboard'))

# ------------------ QR Code Feature ------------------
@app.route('/show_qr')
def show_qr():
    """Page to display the QR code linking to home page"""
    home_url = "https://digitinervate-jaxton-ungloomily.ngrok-free.dev"
    #url_for('home', _external=True)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(home_url)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode("ascii")
    
    return render_template('qr.html', qr_code=img_base64)

# ------------------ SocketIO Events ------------------
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    waiting_tokens = Token.query.filter_by(status="waiting").order_by(Token.id).all()
    called_token = Token.query.filter_by(status="called").first()

    waiting_numbers = [t.number for t in waiting_tokens]
    serving_number = called_token.number if called_token else None

    emit('current_state', {'waiting': waiting_numbers, 'serving': serving_number})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

# ------------------ Run ------------------
if __name__ == '__main__':
    socketio.run(app, debug=True)
