from django.forms import ModelForm

from account_module.models import Score


class ScoreForm(ModelForm):
    class Meta:
        model = Score
        fields = ['quiz_1', 'quiz_2', 'class_activity', 'oral_or_listening', 'final']