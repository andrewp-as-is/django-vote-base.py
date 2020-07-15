from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic.base import View


class VoteViewMixin:
    vote_model = None
    vote_obj = None
    vote_obj_pk = None

    def get_vote_model(self):
        return self.vote_model

    def get_vote_obj(self):
        if not self.request.user.is_authenticated:
            return
        model = self.get_vote_model()
        try:
            return model.objects.get(**self.get_vote_kwargs())
        except model.DoesNotExist:
            pass

    def get_vote_obj_pk(self):
        if self.vote_obj_pk:
            return self.vote_obj_pk
        return self.get_vote_obj().pk

    def get_vote(self):
        if self.request.user.is_authenticated:
            model = self.get_vote_model()
            try:
                return model.objects.get(**self.get_vote_kwargs())
            except model.DoesNotExist:
                pass

    def get_vote_kwargs(self):
        return {
            'created_by': self.request.user,
            'obj_id': self.get_vote_obj_pk()
        }

    def delete_vote(self):
        self.get_vote_model().objects.filter(
            **self.get_vote_kwargs()
        ).delete()

    def create_vote(self, vote):
        defaults = {'vote': vote}
        kwargs = self.get_vote_kwargs()
        self.get_vote_model().objects.get_or_create(defaults, **kwargs)

    def update_vote(self, user, vote):
        self.get_vote_model().objects.filter(
            **self.get_vote_kwargs()
        ).update(vote=vote)

    def vote_down(self):
        vote = self.get_vote()
        if vote and vote.vote == 1:
            self.get_vote_model().objects.filter(pk=vote.pk).update(vote=-1)
        if vote is None:
            self.create_vote(-1)

    def vote_up(self):
        vote = self.get_vote()
        if vote and vote.vote == -1:
            self.get_vote_model().objects.filter(pk=vote.pk).update(vote=1)
        if vote is None:
            self.create_vote(1)

    def vote_down_toggle(self):
        vote = self.get_vote()
        if vote and vote.vote == -1:
            self.get_vote_model().objects.filter(pk=vote.pk).delete()
            return 0
        if vote and vote.vote == 1:
            self.get_vote_model().objects.filter(pk=vote.pk).update(vote=-1)
        if vote is None:
            self.create_vote(-1)
        return -1

    def vote_up_toggle(self):
        vote = self.get_vote()
        if vote and vote.vote == 1:
            self.get_vote_model().objects.filter(pk=vote.pk).delete()
            return 0
        if vote and vote.vote == -1:
            self.get_vote_model().objects.filter(pk=vote.pk).update(vote=1)
        if vote is None:
            self.create_vote(1)
        return 1


class VoteActionViewMixin(LoginRequiredMixin, VoteViewMixin):
    vote_model = None

    def dispatch(self, *args, **kwargs):
        self.vote_obj_pk = self.kwargs['pk']
        return super(VoteActionViewMixin, self).dispatch(*args, **kwargs)

    def get_data(self):
        raise NotImplementedError('get_data() not implemented')


class VoteDownView(VoteActionViewMixin, View):

    def get(self, request, *args, **kwargs):
        self.vote = self.vote_down_toggle()
        return JsonResponse(self.get_data(), status=200)


class VoteUpView(VoteActionViewMixin, View):

    def get(self, request, *args, **kwargs):
        self.vote = self.vote_up_toggle()
        return JsonResponse(self.get_data(), status=200)
