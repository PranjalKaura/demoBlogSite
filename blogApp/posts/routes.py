from flask import Blueprint

from blogApp.models import User, Post
from blogApp.posts.forms import PostForm
from blogApp import db
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required

posts = Blueprint('posts', __name__)

@login_required
@posts.route('/post/new', methods = ['GET', 'POST'])
def newPost():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content = form.content.data, 
                    author = current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been created!", 'success')
        return redirect(url_for('main.home'))
    return render_template('createPost.html', title = 'New Post', 
                           legend = 'New Post', form = form)



@posts.route('/post/<int:postID>')
def post(postID):
    post = Post.query.get_or_404(postID)
    return render_template('post.html', title = post.title, post = post)

@login_required
@posts.route('/post/<int:postID>/update', methods = ['GET', 'POST'])
def updatePost(postID):
    post = Post.query.get_or_404(postID)
    if post.author!=current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', postID = post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('createPost.html', title = 'Update Post', 
                           legend = 'Update Post', form = form)

@login_required
@posts.route('/post/<int:postID>/delete', methods = ['POST'])
def deletePost(postID):
    post = Post.query.get_or_404(postID)
    if post.author!=current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))
