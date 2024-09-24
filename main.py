from datetime import date, datetime
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger, String, Text
from typing import Optional
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, CreateNewList, AddItemForm 
import os



from dotenv import load_dotenv
load_dotenv()


# ****************************************** Web Server Config ******************************************
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# ****************************************** Create Database ******************************************
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CONFIGURE TABLES
class ToDoItem(db.Model):
    __tablename__ = "todoitems"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    description: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    #add later
    #added_date      : Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()),
    #completed_date  : Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()),
    todo_list_id: Mapped[Optional[int]] = mapped_column(ForeignKey("todolists.id"), nullable=False)
    #category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)
    status  : Mapped[bool] = mapped_column(unique=False, default=True)
    archive :  Mapped[bool] =  mapped_column(unique=False, default=False)
    #add status!!!!!!

    
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    todolists= relationship("ToDoList", back_populates="author") # back populates the author of the to do list
    #categories= relationship("Category", back_populates="author") # back poluates the author of the category
    

#Name of the List for the item in todoitems
class ToDoList(db.Model):
    __tablename__ = "todolists"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="todolists") # back populates the todo lists the user authors
    description: Mapped[str] = mapped_column(String(50), unique=False, nullable=False)


# #Category of the item in todoitems
# class Category(db.Model):
#     __tablename__ = "categories"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
#     author = relationship("User", back_populates="categories")# back populates the categories the user authors
#     description: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
#     icon: Mapped[str] = mapped_column(String(50), nullable=True)


with app.app_context():
    db.create_all()


# ****************************************** Web redirects ******************************************
# ************* Users and Login *************


# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("todo"))
    return render_template("register.html", form=form, current_user=current_user.id)


@app.route('/')
def home():
    return render_template("index.html", current_user=current_user.id)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('todo'))

    return render_template("login.html", form=form, current_user=current_user.id)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'),current_user=current_user.id)


# ************* App *************

@app.route('/todo')
def todo():
    result = db.session.execute(db.select(ToDoList))
    lists  = result.scalars().all()
    return render_template("todo.html", todo_lists = lists, current_user=current_user.id)


@app.route('/newlist', methods=["GET", "POST"])
def new_list():
    new_list_form = CreateNewList()
    if new_list_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))
        
        print(f"Adding To Do List: author_id:{current_user.id}, description:{new_list_form.description.data}")
        new_list = ToDoList(author_id = current_user.id, description = new_list_form.description.data)
        db.session.add(new_list)
        db.session.commit()
        #redirect to newly created list
        #return render_template("addeditlist.html", id = ??, current_user=current_user.id)
        return redirect(url_for("todo", current_user=current_user.id))
        
    return render_template("newlist.html", form=new_list_form, current_user=current_user.id)


# @app.route('/newcat')
# def new_category():
#     return render_template("newcat.html", current_user=current_user.id)

@app.route('/addeditlist/<int:list_id>', methods=["GET", "POST"])
def add_edit_list(list_id):
    #get list
    requested_list = db.get_or_404(ToDoList, list_id)
    
    #get list Items
    requested_list_items = db.session.execute(db.select(ToDoItem).where(ToDoItem.todo_list_id == list_id, ToDoItem.status == True)).scalars().all()
    requested_completed_items = db.session.execute(db.select(ToDoItem).where(ToDoItem.todo_list_id == list_id, ToDoItem.status == False)).scalars().all()

    add_items_form = AddItemForm()
    if add_items_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))
        
        print(f"Adding Items to To Do List: list_id:{list_id}:")
        new_items = []
        if str.strip(add_items_form.description_1.data) != "":
            print(f"ToDo(1):{add_items_form.description_1.data}")
            new_items.append(ToDoItem(author_id = current_user.id,todo_list_id = list_id, description = add_items_form.description_1.data))
        
        if str.strip(add_items_form.description_2.data) != "":
            print(f"ToDo(2):{add_items_form.description_2.data}")
            new_items.append( ToDoItem(author_id = current_user.id,todo_list_id = list_id, description = add_items_form.description_2.data))
        
        if str.strip(add_items_form.description_3.data) != "":
            print(f"ToDo(3):{add_items_form.description_3.data}")
            new_items.append( ToDoItem(author_id = current_user.id,todo_list_id = list_id, description = add_items_form.description_3.data))
          
        if len(new_items) > 0:
            db.session.bulk_save_objects(new_items)
            db.session.commit()

        return redirect(url_for("add_edit_list", list_id = list_id, current_user=current_user.id))
        

    return render_template("addeditlist.html",list=requested_list, list_items=requested_list_items, completed_items=requested_completed_items,add_form = add_items_form, current_user=current_user.id)


@app.route("/complete-item/<int:list_id>/<int:item_id>", methods=["GET", "POST"])
def complete_item(list_id, item_id):
    if not current_user.is_authenticated:
        flash("You need to login or register to comment.")
        return redirect(url_for("login"))

    item_to_archive= db.get_or_404(ToDoItem, item_id)

    if item_to_archive.author_id == current_user.id:
        item_to_archive.status = False
        db.session.commit()
        return redirect(url_for('add_edit_list', list_id = list_id))
    else:
        flash("You cannot complete other users items!")
        return redirect(url_for('add_edit_list', list_id = list_id))
    


@app.route("/restore-item/<int:list_id>/<int:item_id>", methods=["GET", "POST"])
def restore_item(list_id, item_id):
    if not current_user.is_authenticated:
        flash("You need to login or register to comment.")
        return redirect(url_for("login"))

    item_to_archive= db.get_or_404(ToDoItem, item_id)

    if item_to_archive.author_id == current_user.id:
        item_to_archive.status = True
        db.session.commit()
        return redirect(url_for('add_edit_list', list_id = list_id))
    else:
        flash("You cannot complete other users items!")
        return redirect(url_for('add_edit_list', list_id = list_id))


@app.route("/delete-item/<int:list_id>/<int:item_id>", methods=["GET", "POST"])
def delete_item(list_id, item_id):
    if not current_user.is_authenticated:
        flash("You need to login or register to comment.")
        return redirect(url_for("login"))

    item_to_archive= db.get_or_404(ToDoItem, item_id)

    if item_to_archive.author_id == current_user.id:
        item_to_archive.archive = True
        db.session.commit()
        return redirect(url_for('add_edit_list', list_id = list_id))
    else:
        flash("You cannot complete other users items!")
        return redirect(url_for('add_edit_list', list_id = list_id))


@app.route("/undelete-item/<int:list_id>/<int:item_id>", methods=["GET", "POST"])
def undelete_item(list_id, item_id):
    if not current_user.is_authenticated:
        flash("You need to login or register to comment.")
        return redirect(url_for("login"))

    item_to_archive= db.get_or_404(ToDoItem, item_id)

    if item_to_archive.author_id == current_user.id:
        item_to_archive.archive = False
        db.session.commit()
        return redirect(url_for('add_edit_list', list_id = list_id))
    else:
        flash("You cannot complete other users items!")
        return redirect(url_for('add_edit_list', list_id = list_id))


# ************* Site *************

@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user.id)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("contact.html", current_user=current_user.id)
    



    








    

if __name__ == "__main__":
    app.run(debug=False, port=5000)