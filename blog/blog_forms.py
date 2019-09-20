from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, validators


class PostForm(FlaskForm):
    title = StringField(u'Post Title', validators=[validators.DataRequired()])
    body = CKEditorField('body', validators=[validators.DataRequired()])
    tags = StringField(u'Tags', validators=[])
    submit = SubmitField('Save Post')
