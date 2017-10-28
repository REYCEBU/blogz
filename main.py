from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Baboy@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login')
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup',methods=['POST', 'GET'])
def sign_up():
    
   #We got the info from the form submitted by the user

    username = request.form['username']
    password = request.form['password']
    verify = request.form['verify']
    email = request.form['email']

   #Storage for our error messages

    username_error = ""
    password_error = ""
    verify_error = ""
    email_error = ""

    if username == "" or " " in username or len(username) < 3 or len(username) > 20:
       username_error = "Invalid username"

    if password == "" or " " in password or len(password) < 3 or len(password) > 20:
       password_error = "Invalid password"

    if verify == "" or verify != password:
        verify_error = "Invalid verification"

    if email != "":
       if "@" not in email or "." not in email or " " in email or len(email) < 3 or len(email) > 20:
               email_error = "Invalid email"

    if email_error == "" and username_error == "" and verify_error == "" and password_error == "":
       return render_template("welcome.html", username = username)

    else:
       return render_template("index.html", username_error = username_error
                                          , password_error = password_error
                                          , verify_error = verify_error
                                          , email_error = email_error
                                          , username = username
                                          , email = email)


@app.route('/logout')
def logout():
   # del session('username')
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def index():

    if request.args.get('id'):
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)

        return render_template('blogentry.html', blog=blog)

   # else:
    
       # if request.args.get('owner')
            #owner_id = request.args.get('owner')
           # blog = Blog.query.get(owner_id)

    else:
        blogs = Blog.query.all()

        return render_template('blog.html', title="Build A Blog", blog=blogs)

@app.route('/newpost', methods=['GET', 'POST'])
def add_blog():
    if request.method == 'GET':
        return render_template('newpost.html', title="Add Blog Entry")

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ""
        body_error = ""

        if len(blog_title) < 1:
            title_error = "Invalid title"   

        if len(blog_body) < 1:
            body_error = "Invalid Body"

        if not title_error and not body_error:
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            query_param_url = "/blog?id=" + str(new_blog.id)
            return redirect(query_param_url)

        else:
            return render_template('newpost.html', title_error = title_error, body_error = body_error)
              
    
    

if __name__ == '__main__':
    app.run()