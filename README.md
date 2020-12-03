<!--
https://readme42.com
-->


[![](https://img.shields.io/pypi/v/django-vote-base.svg?maxAge=3600)](https://pypi.org/project/django-vote-base/)
[![](https://img.shields.io/badge/License-Unlicense-blue.svg?longCache=True)](https://unlicense.org/)
[![](https://github.com/andrewp-as-is/django-vote-base.py/workflows/tests42/badge.svg)](https://github.com/andrewp-as-is/django-vote-base.py/actions)

### Installation
```bash
$ [sudo] pip install django-vote-base
```

##### `settings.py`
```python
INSTALLED_APPS+=['django_vote_base']
```

##### `models.py`
```python
from django.db import models
from django_vote_base.models import VoteModel

class CollectionVote(VoteModel):
    obj = models.ForeignKey(
        'Collection', related_name="vote_set", on_delete=models.CASCADE)

    class Meta:
        unique_together = [('obj', 'created_by')]

class Collection(models.Model):
    votes_up_count = models.IntegerField(null=True)
    votes_down_count = models.IntegerField(null=True)
    votes_score = models.IntegerField(null=True)

    def get_vote_down_url(self):
        return '/vote/collection/down/%s' % (self.pk,)

    def get_vote_up_url(self):
        return '/vote/collection/up/%s' % (self.pk,)
```

##### `urls.py`
```python
from django.urls import include, path

import views

urlpatterns = [
    path('vote/collection/down/<int:pk>', views.VoteDownView.as_view(), name='down'),
    path('vote/collection/up/<int:pk>', views.VoteUpView.as_view(), name='up')
]
```

##### `views.py`
`DetailView` - context variables `{{ vote_obj }}` and `{{ vote }}`
```python
from apps.collections.models import Collection, CollectionVote
from django_vote_base.views import VoteViewMixin

class VoteDetailView(BookmarkViewMixin):
    vote_model = CollectionVote
```

`XMLHttpRequest` view
```python
from django_vote_base.views import VoteDownView, VoteUpView
from apps.core.collections.models import Collection, CollectionVote

class CollectionVoteViewMixin:
    vote_model = CollectionVote

    def get_data(self):
        collection = Collection.objects.get(pk=self.kwargs['pk'])
        return {
            'vote': self.vote,
            'votes_up_count': collection.votes_up_count,
            'votes_down_count': collection.votes_down_count,
            'votes_score': collection.votes_score
        }

class VoteDownView(CollectionVoteViewMixin, VoteDownView):
    pass

class VoteUpView(CollectionVoteViewMixin, VoteUpView):
    pass

```

`ListView` prefetch user bookmarks
```python
from django.db.models import Prefetch
from django.views.generic.list import ListView
from apps.collections.models import Collection, CollectionVote

class CollectionListView(ListView):
    def get_queryset(self, **kwargs):
        qs = Collection.objects.all()
        if self.request.user.is_authenticated:
            qs = qs.prefetch_related(
                Prefetch("vote_set", queryset=CollectionVote.objects.filter(created_by=self.request.user),to_attr='votes')
            )
        return qs
```

##### Templates
```html
<a data-id="{{ vote_obj.pk }}" class="vote-up-btn {% if vote and vote.vote > 0 %}selected{% endif %}" {% if request.user.is_authenticated %}data-href="{{ vote_obj.get_vote_up_url }}"{% else %}href="{% url 'login' %}?next={{ request.path }}"{% endif %}>
</a>

<a data-id="{{ vote_obj.pk }}" class="votes-score">{{ vote_obj.votes_score|default:"0" }}</a>

<a data-id="{{ vote_obj.pk }}" class="vote-down-btn {% if vote and vote.vote < 0 %}selected{% endif %}" {% if request.user.is_authenticated %}data-href="{{ vote_obj.get_vote_down_url }}"{% else %}href="{% url 'login' %}?next={{ request.path }}"{% endif %}>
</a>
```

##### JavaScript
```javascript
const vote_buttons = document.querySelectorAll("a.vote-up-btn, a.vote-down-btn");
for (const button of vote_buttons) {
  button.addEventListener('click', function(event) {
    event.preventDefault();
    data_id = button.getAttribute('data-id');

    var vote_down_btn = document.querySelector(".vote-down-btn[data-id='"+data_id+"']");
    var vote_up_btn = document.querySelector(".vote-up-btn[data-id='"+data_id+"']");
    var votes_score = document.querySelector(".votes-score[data-id='"+data_id+"']");

    var xhr = new XMLHttpRequest();
    xhr.open('GET', button.getAttribute('data-href'));
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.responseType = 'json';
    xhr.onload = function() {
        if (xhr.status != 200) {
            console. error(`Error ${xhr.status}: ${xhr.statusText}`);
        }
        if (xhr.status == 200) {
            votes_score.innerHTML=xhr.response.votes_score;
        }
    };
    xhr.send();
  })
}
```

<p align="center">
    <a href="https://readme42.com/">readme42.com</a>
</p>
