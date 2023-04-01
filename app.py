# Import necessary modules and classes
from flask import Flask, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag

# Create the Flask application instance and set the configuration settings
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ihaveasecret'

# Create an instance of the DebugToolbarExtension and pass in the Flask app
toolbar = DebugToolbarExtension(app)

# Connect the Flask app to the database and create any missing database tables
connect_db(app)
db.create_all()

# Define the route for the homepage
@app.route('/')
def root():
    """Show recent list of posts, most-recent first."""
    
    # Query the database for the most recent 5 posts and render the template with those posts
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template("posts/homepage.html", posts=posts)

# Define an error handler for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""
    
    # Render a custom 404 template
    return render_template('404.html'), 404


##############################################################################
# User route

@app.route('/users')
def users_index():
    """Show a page with info on all users"""

    # Query all users from the database and order them by last name and first name
    users = User.query.order_by(User.last_name, User.first_name).all()

    # Render the HTML template for the users index page and pass in the users list
    return render_template('users/index.html', users=users)


@app.route('/users/new', methods=["GET"])
def users_new_form():
    """Show a form to create a new user"""

    # Render the HTML template for the new user form page
    return render_template('users/new.html')


@app.route("/users/new", methods=["POST"])
def users_new():
    """Handle form submission for creating a new user"""

    # Create a new User object with data from the form
    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url'] or None)

    # Add the new user to the database and commit the transaction
    db.session.add(new_user)
    db.session.commit()

    # Flash a success message with the new user's full name
    flash(f"User {new_user.full_name} added.")

    # Redirect the user to the users index page
    return redirect("/users")


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show a page with info on a specific user"""

    # Get the User object with the specified ID from the database, or show a 404 error
    user = User.query.get_or_404(user_id)

    # Render the HTML template for the user show page and pass in the user object
    return render_template('users/show.html', user=user)


@app.route('/users/<int:user_id>/edit')
def users_edit(user_id):
    """Show a form to edit an existing user"""

    # Get the User object with the specified ID from the database, or show a 404 error
    user = User.query.get_or_404(user_id)

    # Render the HTML template for the user edit page and pass in the user object
    return render_template('users/edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["POST"])
def users_update(user_id):
    """Handle form submission for updating an existing user"""

    # Get the User object with the specified ID from the database, or show a 404 error
    user = User.query.get_or_404(user_id)

    # Update the User object with data from the form
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    # Add the updated user to the database and commit the transaction
    db.session.add(user)
    db.session.commit()

    # Flash a success message with the updated user's full name
    flash(f"User {user.full_name} edited.")

    # Redirect the user to the user show page
    return redirect(f"/users/{user_id}")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def users_destroy(user_id):
    """Handle form submission for deleting an existing user"""

    # Get the User object with the specified ID from the database, or show a 404 error
    user = User.query.get_or_404(user_id)

    # Delete the User object from the database and commit the transaction
    db.session.delete(user)
    db.session.commit()

    # Flash a success message with the deleted user's full name
    flash(f"User {user.full_name} deleted.")

    return redirect("/users")


##############################################################################
# Posts route

@app.route('/users/<int:user_id>/posts/new')
def posts_new_form(user_id):
    """Show a form to create a new post for a specific user"""
    # get user with the given user_id or return a 404 error if not found
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    # render the new post form template and pass the user to the template
    return render_template('posts/new.html', user=user, tags=tags)

@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def posts_new(user_id):
    """Handle form submission for creating a new post for a specific user"""
    # get user with the given user_id or return a 404 error if not found
    user = User.query.get_or_404(user_id)
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    # create a new post with the title and content from the form, and associate it with the user
    new_post = Post(title=request.form['title'],
                    content=request.form['content'],
                    user=user,
                    tags = tags)
    # add the new post to the database session and commit the changes
    db.session.add(new_post)
    db.session.commit()
    # flash a success message to display on the next page
    flash(f"Post '{new_post.title}' added.")
    # redirect to the user's profile page
    return redirect(f"/users/{user_id}")

@app.route('/posts/<int:post_id>')
def posts_show(post_id):
    """Show a page with info on a specific post"""
    # get the post with the given post_id or return a 404 error if not found
    post = Post.query.get_or_404(post_id)
    # render the post show template and pass the post to the template
    return render_template('posts/show.html', post=post)

@app.route('/posts/<int:post_id>/edit')
def posts_edit(post_id):
    """Show a form to edit an existing post"""
    # get the post with the given post_id or return a 404 error if not found
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    # render the post edit template and pass the post to the template
    return render_template('posts/edit.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def posts_update(post_id):
    """Handle form submission for updating an existing post"""
    # get the post with the given post_id or return a 404 error if not found
    post = Post.query.get_or_404(post_id)
    # update the post with the title and content from the form
    post.title = request.form['title']
    post.content = request.form['content']
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    # add the updated post to the database session and commit the changes
    db.session.add(post)
    db.session.commit()
    # flash a success message to display on the next page
    flash(f"Post '{post.title}' edited.")
    # redirect to the user's profile page
    return redirect(f"/users/{post.user_id}")

@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def posts_destroy(post_id):
    """Handle form submission for deleting an existing post"""
    # get the post with the given post_id or return a 404 error if not found
    post = Post.query.get_or_404(post_id)
    # delete the post from the database session and commit the changes
    db.session.delete(post)
    db.session.commit()
    # flash a success message to display on the next page
    flash(f"Post '{post.title} deleted.")
    # redirect to the user's profile page
    return redirect(f"/users/{post.user_id}")

##############################################################################
# Tags route


@app.route('/tags')
def tags_index():
    """Show a page with info on all tags"""

    tags = Tag.query.all()
    return render_template('tags/index.html', tags=tags)


@app.route('/tags/new')
def tags_new_form():
    """Show a form to create a new tag"""

    posts = Post.query.all()
    return render_template('tags/new.html', posts=posts)


@app.route("/tags/new", methods=["POST"])
def tags_new():
    """Handle form submission for creating a new tag"""

    post_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    new_tag = Tag(name=request.form['name'], posts=posts)

    db.session.add(new_tag)
    db.session.commit()
    flash(f"Tag '{new_tag.name}' added.")

    return redirect("/tags")


@app.route('/tags/<int:tag_id>')
def tags_show(tag_id):
    """Show a page with info on a specific tag"""

    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/show.html', tag=tag)


@app.route('/tags/<int:tag_id>/edit')
def tags_edit_form(tag_id):
    """Show a form to edit an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('tags/edit.html', tag=tag, posts=posts)


@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def tags_edit(tag_id):
    """Handle form submission for updating an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']
    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' edited.")

    return redirect("/tags")


@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def tags_destroy(tag_id):
    """Handle form submission for deleting an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' deleted.")

    return redirect("/tags")