from blogApp.models import User, Post
from blogApp import app, db, bcrypt, mail
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
import secrets
from PIL import Image
import os

app.app_context().push()
db.create_all()





