from blogApp import app, mail
from flask import url_for
from flask_mail import Message
import secrets
from PIL import Image
import os


def savePicture(formPicture):
    randomHex = secrets.token_hex(8)
    _, fileExt = os.path.splitext(formPicture.filename)
    randomFileName = randomHex + fileExt
    filePath = os.path.join(app.root_path, 'static/profile_pics', randomFileName)
    #resizing image
    output_size = (125, 125)
    i = Image.open(formPicture)
    i.thumbnail(output_size)
    i.save(filePath)

    return randomFileName


def sendResetEmail(user):
    token = user.getResetToken()
    msg = Message('Password Reset Request', sender='pranjalkaura22@gmail.com', 
                  recipients=[user.email])
    msg.body = f''' To reset your password visit the following link:
    {url_for('users.resetPassword', token = token, _external = True)}

    If you did not make this request, please ignore this message.
    '''
    mail.send(msg)