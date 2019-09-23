from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import SubmitField, StringField, validators, FileField


class PostForm(FlaskForm):
    title = StringField(u'Post Title', validators=[validators.DataRequired()])
    post_image_file = FileField('Post head picture', validators=[FileAllowed(['jpg', 'png', 'webp'])])
    body = CKEditorField('body', validators=[validators.DataRequired()])
    tags = StringField(u'Tags', validators=[])
    submit = SubmitField('Save Post')
