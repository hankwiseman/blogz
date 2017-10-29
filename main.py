from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:MyNewPass@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'user_list', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data
            # if the user typed nothing at all, redirect and tell them the error
        if len(username) < 3 or len(username) > 20:
            username_error = "The username is not between 3 and 20 characters."
            return render_template('signup.html', username_error=username_error)

        if len(password) < 3 or len(password) > 20:
            password_error = "The password is not between 3 and 20 characters."
            return render_template('signup.html', password_error=password_error)

        if password != verify:
            verify_error = "The passwords do not match"
            return render_template('index.html', verify_error=verify_error)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/login')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('newpost.html')

@app.route('/blog', methods=['POST', 'GET'])
def index():

    blogs = Blog.query.all()
    
    userid = request.args.get('user')
    if userid:
        blog_post = Blog.query.filter_by(owner_id=userid).all()
        return render_template('blog.html',blogs=blog_post)


    blog_id = request.args.get('id')
    
    if blog_id:
        blog_post = Blog.query.get(blog_id)
        return render_template('blog_post.html',blog_post=blog_post)

    return render_template('blog.html',title="Blog List", 
        blogs=blogs)

# Blog.query.filter_by(id=int(request.args.get('id'))).all()
@app.route('/newpost', methods=['POST', 'GET'])
def delete_task():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        if blog_title == "":
            title_error = "The blog post must have a title!"
            return render_template('newpost.html',title_error=title_error)
        blog_content = request.form['form']
        if blog_content == "":
            content_error = "The blog post must have content!"
            return render_template('newpost.html',content_error=content_error)
        new_blog = Blog(title =blog_title, body =blog_content, owner = owner)
        db.session.add(new_blog)
        db.session.commit()
        new_blog_link = '/blog?id='+str(new_blog.id)
        return redirect(new_blog_link)

    return render_template('newpost.html')

@app.route('/', methods=['POST', 'GET'])
def user_list():
    users = User.query.all()

    return render_template('index.html',users=users)

if __name__ == '__main__':
    app.run()