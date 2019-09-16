from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, validators


class PostForm(FlaskForm):
    title = StringField(u'Post Title', validators=[validators.DataRequired()])
    body = TextAreaField(u'Post Body', validators=[validators.DataRequired()])
    tags = StringField(u'Tags', validators=[])
    submit = SubmitField('Save Post')
