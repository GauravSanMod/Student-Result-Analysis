from flask import Flask,render_template, request, redirect, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import pickle, secrets, bcrypt, io, base64
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required


model = pickle.load(open("svm_model.pkl", "rb"))

#secret Key generator
def generate_secret_key(length):
    return secrets.token_hex(length)
secret_key = generate_secret_key(64)

app = Flask(__name__)

app.app_context().push() # use to push application context onto context stack

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587 #465 is used with ssl
app.config['MAIL_USERNAME'] = 'gaurav8bp2@gmail.com'
app.config['MAIL_PASSWORD'] = 'dummy' 
app.config['MAIL_USE_SSL'] = False # tls is preferred over ssl 
app.config['MAIL_USE_TLS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = secret_key #production change
#Pdf size
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 #5MB


#instance of mail
mail = Mail(app)

#instance of database
db = SQLAlchemy(app)

#instance of LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('delay'))


#Student Table
class student(db.Model, UserMixin):
    student_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False , unique=True)
    college = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __init__(self, name, email, college, password):
        self.name = name
        self.email = email
        self.college = college
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

    def get_id(self):
        return f"student_{self.student_id}"


#Admin Table
class Admin(db.Model, UserMixin):
    admin_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False , unique=True)
    college = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __init__(self, name, email, college, password):
        self.name = name
        self.email = email
        self.college = college
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

    def get_id(self):
        return f"admin_{self.admin_id}"


#Result Table
class result(db.Model):
    result_id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    java = db.Column(db.Integer, nullable=False)
    python = db.Column(db.Integer, nullable=False)
    spm = db.Column(db.Integer, nullable=False)
    ot = db.Column(db.Integer, nullable=False)
    ait = db.Column(db.Integer, nullable=False)
    adbms = db.Column(db.Integer, nullable=False)
    prediction = db.Column(db.Integer, nullable=False)
    student = db.relationship('student', backref=db.backref('results', lazy=True))

    def __init__(self, student_id, java, python, spm, ot, ait, adbms, prediction):
        self.student_id = student_id
        self.java = java
        self.python = python
        self.spm = spm
        self.ot = ot
        self.ait = ait
        self.adbms = adbms
        self.prediction = prediction


#Intervention Table
class Intervention(db.Model):
    inter_id = db.Column(db.Integer, primary_key=True)
    student_email = db.Column(db.String(50), nullable=False)
    admin_email = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(10), nullable=False)

    def __init__(self,student_email, admin_email, status):
        self.student_email = student_email
        self.admin_email = admin_email
        self.status = status


# User loader callback
@login_manager.user_loader
def load_user(user_id):
    table_name, actual_user_id = user_id.split("_",1)
    if table_name == 'student':
        return student.query.get(int(actual_user_id))
    elif table_name == 'admin':
        return Admin.query.get(int(actual_user_id))
    return None

#Home Route
@app.route('/')
def index():
    svm = model['model']
    X_test = model['x_test']
    y_test = model['y_test']
    y_pred = svm.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6,4))
    c_label = ['Fail', 'Pass']
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, xticklabels=c_label, yticklabels=c_label)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion_Matrix")
    img_data = io.BytesIO() 
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    encoded_img = base64.b64encode(img_data.read()).decode('utf-8')
    return render_template('index.html', encoded_img = encoded_img)

#Home Contact
@app.route('/contact', methods = ["POST", "GET"])
def contact():
    if request.method == 'POST':
        name = request.form['fullname']
        email = request.form['email']
        phone_no = request.form['phone']
        subject = request.form['subject']
        message = request.form['message']
        msg = Message(subject=subject, sender=name, recipients=['gaurav8bp2@gmail.com','tanayaaswale@gmail.com'])
        msg.body = f" Mail ID: {email} \n Phone No: {phone_no} \n Body: {message}"
        mail.send(msg)
        return "Email Sent Successfully"
    else:
        return render_template("contact.html")

#Home About
@app.route('/about')
def about():
    return render_template("about.html")

#Student Prediction
@app.route('/predict', methods=['POST', 'GET'])
@login_required
def predict():
    if request.method=='POST':
        java = request.form['java']
        python = request.form['python']
        spm = request.form['spm']
        ot = request.form['ot']
        ait = request.form['ait']
        adbms = request.form['adbms']
        arr = [[java, python, spm, ot, ait,adbms]]
        svm = model['model']
        pred = svm.predict(arr)
        if pred==[1]:
            prediction=1
        else:
            prediction=0
        new_prediction = result(student_id =current_user.student_id, java=java, python=python, spm=spm, ot=ot, ait=ait, adbms=adbms, prediction=prediction)
        db.session.add(new_prediction)
        db.session.commit()
        return render_template("result.html", data = pred)
    else:
        return render_template("predict.html")

#Student Related Content Start
@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    elif request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        college = request.form['college']
        password = request.form['password']
        c_password = request.form['c_password']
        if password == c_password:
            new_user = student(name=name, email=email, college=college, password=password)
            db.session.add(new_user)
            db.session.commit()
        else:
            return "<h1>Password and confirm password are not matching</h1>"
        return redirect(url_for('login'))
    else:
        return render_template("register.html")

#student Login
@app.route('/login', methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = student.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return "<h1>Invalid Email or Password</h1>"
    else:
        return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
#Student Related Contain Ended

#Admin
@app.route('/admin_index')
@login_required
def admin_index():
    if current_user.is_authenticated:
        return render_template("/admin_index.html")
    else:
        return render_template("/admin_login.html")

@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect('/admin_index')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin_user = Admin.query.filter_by(email=email).first()
        if admin_user and admin_user.check_password(password):
            login_user(admin_user)
            return redirect(url_for('admin_index'))
        else:
            return "<h1>Invalid Email or Password</h1>"
    else:
        return render_template("admin_login.html")

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if current_user.is_authenticated:
        return redirect('/admin_index')
    elif request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        college = request.form['college']
        password = request.form['password']
        confirm_password = request.form['c_password']
        if password == confirm_password:
            new_user = Admin(name=name, email=email, college=college, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/admin_login')
        else:
            return "<h1>Password and confirm password are not Matching</h1>"
    else:
        return render_template("admin_register.html")

@app.route('/view_result')
@login_required
def view_result():
    result_student = db.session.query(result, student).join(student).all()
    return render_template("view_result.html", result_student=result_student)

@app.route('/m_intervention', methods=['GET', 'POST'])
@login_required
def m_intervention():
    if request.method == 'POST':
        student_email = request.form["email"]
        status = "Assigned"
        admin_email = current_user.email
        data = Intervention(student_email=str(student_email), admin_email = admin_email, status=status)
        db.session.add(data)
        db.session.commit()
        subject = request.form['subject']
        pdf_file = request.files.get('file')
        msg = Message(subject=subject, sender=admin_email, recipients=[str(student_email)])
        if pdf_file and pdf_file.filename.endswith('.pdf'):
            msg.attach(pdf_file.filename, 'application/pdf', pdf_file.read())
        suggestion = request.form['suggest']
        msg.body = f"Mail ID: {admin_email} \nSubject:{subject} \nSuggestion: {suggestion}"
        mail.send(msg)
        return "Email Sent Successfully"
    else:
        data = db.session.query(Intervention).all()
        return render_template("m_intervention.html", data=data)


@app.route('/admin_logout')
@login_required
def admin_logout():
    logout_user()
    return redirect('/admin_login')

@app.route('/delay')
def delay():
    return render_template("delay.html")

if __name__ == "__main__":
    app.run(debug=True)#production change
