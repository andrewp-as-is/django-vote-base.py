from django.conf import settings
from django.db import models


class VoteModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='+', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    vote = models.IntegerField()
    # obj = models.ForeignKey(..., on_delete = models.CASCADE)

    class Meta:
        abstract = True


class VoteMixin:
    vote_model = None

    def get_vote_model(self):
        return self.vote_model

    def get_vote(self, user):
        if user.is_authenticated:
            model = self.get_vote_model()
            try:
                return model.objects.get(created_by=user, obj_id=self.pk)
            except model.DoesNotExist:
                pass

    def delete_vote(self, user):
        self.get_vote_model().objects.filter(
            created_by=user, obj_id=self.pk
        ).delete()

    def create_vote(self, user, vote):
        defaults = {'vote': vote}
        kwargs = {'created_by': user, 'obj_id': self.pk}
        self.get_vote_model().objects.get_or_create(defaults, **kwargs)

    def update_vote(self, user, vote):
        self.get_vote_model().objects.filter(
            created_by=user, obj_id=self.pk
        ).update(vote=vote)

    def vote_down(self, user):
        vote = self.get_vote(user)
        if vote and vote.vote == 1:
            self.get_vote_model().objects.filter(pk=vote.pk).update(vote=-1)
        if vote is None:
            self.create_vote(user, -1)

    def vote_up(self, user):
        vote = self.get_vote(user)
        if vote and vote.vote == -1:
            self.get_vote_model().objects.filter(pk=vote.pk).update(vote=1)
        if vote is None:
            self.create_vote(user, 1)


"""
from django.db import models
from django_vote_base.models import VoteModel

class PostVote(VoteModel):
    obj = models.ForeignKey(
        'Post', related_name = "+", on_delete = models.CASCADE)

    class Meta:
        unique_together = [('obj', 'created_by')]


class Post(VoteMixin,models.Model):
    ...
    votes_down_count = models.IntegerField(null=True)
    votes_up_count = models.IntegerField(null=True)
    votes_score = models.IntegerField(null=True)

    vote_model = PostVote
"""
