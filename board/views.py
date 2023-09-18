from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from .models import Post, Response, Reply, Category
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from .forms import PostForm, PostResponseForm, ReplyForm
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormMixin
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import User
from .filters import ResponseFilter
from django.http import HttpResponseRedirect
from django.db.models import Q

class PostList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 6


class PostDetailView(DetailView, FormMixin):
    template_name = 'post.html'
    model = Post
    context_object_name = 'post_detail'

    form_class = PostResponseForm


    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        response = form.save(commit=False)
        response.responseUser = self.request.user
        response.responsePost = Post.objects.get(id=self.kwargs['pk'])
        author_post = Post.objects.get(id=self.kwargs['pk'])
        user_post = author_post.author
        user_email = user_post.email
        response.save()
        subject = 'Пользователь оставил отклик на ваше объявление'
        message = f'Пользователь {response.responseUser.username} оставил ответ на ваш отклик.'
        from_email = 'managernewssk@mail.ru'
        recipient_list = [user_email]

        send_mail(subject, message, from_email, recipient_list)

        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse('post_detail', args=[self.kwargs['pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['responses'] = Response.objects.filter(responsePost=self.object)
        return context


class ResponseListView(DetailView, FormMixin):
    model = Response
    template_name = 'post.html'
    context_object_name = 'response'
    form_class = ReplyForm


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['responseUser'] = self.request.user

        return context

    # def get(self, request, *args, **kwargs):
    #     # Обработка GET-запроса
    #     # Здесь можете добавить логику для получения и отображения данных
    #     return render(request, self.template_name, {'form': PostResponseForm()})
    #
    # def post(self, request, *args, **kwargs):
    #     # Обработка POST-запроса
    #     form = PostResponseForm(request.POST)
    #     if form.is_valid():
    #         response = form.save()
    #         # Дополнительная логика после успешного сохранения
    #         return redirect('/posts')

        # # Если форма не валидна, вернуть обратно с ошибками
        # return render(request, self.template_name, {'form': form})

class PostCreateView(LoginRequiredMixin, CreateView):
    #print('trdhc')
    template_name = 'post_create.html'
    form_class = PostForm
    permission_required = ('post.add_post',)
    success_url = '/posts/'


    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = User.objects.get(id=self.request.user.id)

        # category_id = self.request.POST.get('category_id')
        # category = Category.objects.get(pk=category_id)
        # print(category)

        post.save()
        #post.postCategory.add(category)
        #print(category)
        return super().form_valid(form)

    # def post(self, request, *args, **kwargs):
    #     form = self.form_class(request.POST)
    #     if form.is_valid(): # если пользователь ввёл всё правильно и нигде не накосячил, то сохраняем новый товар
    #         form.save()
    #     return super().form_valid(form)
    #     # else:
    #     #     return HttpResponseBadRequest("Form is not valid")
    #


class PostUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'post_update.html'
    form_class = PostForm
    permission_required = ('post.change_post')


    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

    # def form_valid(self, form):
    #     # Проверяем, если объект существует (редактирование), сохраняем изменения,
    #     # в противном случае создаем новый пост
    #     if self.object:
    #         self.object = form.save()
    #     # else:
    #     #     self.object = form.save(commit=False)
    #     #     self.object.author = self.request.user
    #     #     self.object.save()
    #     return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'post_delete.html'
    model = Post
    queryset = Post.objects.all()
    success_url = reverse_lazy('posts_list')
    permission_required = 'post.delete_post'


class PrivatelistView(ListView, FormMixin):
        model = Response
        template_name = 'private_response.html'
        context_object_name = 'responses'
        form_class = ReplyForm
        success_url = '/index/'


        def get_queryset(self):
            user = self.request.user
            responses_by_user = Response.objects.filter(responsePost__author=user)
            user_responses_to_other_ads = Response.objects.filter(responseUser=user)


            combined_responses = user_responses_to_other_ads | responses_by_user
            combined_responses = combined_responses.order_by('-dateCreation')

            return combined_responses

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['user'] = self.request.user
            return context

        def post(self, request, *args, **kwargs):
            form = ReplyForm(request.POST)

            if form.is_valid():
                return self.form_valid(form)
            return self.form_invalid(form)

        def form_valid(self, form):
            reply = form.save(commit=False)
            reply.user = self.request.user

            reply.response_reply_id = int(self.request.POST.get("response_post_id"))
            print(reply.response_reply_id)
            reply.replied_to_user_id = int(self.request.POST.get("response_user_id"))

            replied_to_user = User.objects.get(id=reply.replied_to_user_id)

            print(reply.replied_to_user_id)
            reply.save()
            subject = 'Новый ответ на ваш отклик'
            message = f'Пользователь {reply.user.username} оставил ответ на ваш отклик.'
            from_email = 'managernewssk@mail.ru'
            recipient_list = [replied_to_user.email]

            send_mail(subject, message, from_email, recipient_list)
            return super().form_valid(form)


        #
        # # Перенаправляем пользователя обратно на страницу откликов
        # return redirect('privatelist')



        # def post(self, request, *args, **kwargs):
        #     form = ReplyForm(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса
        #
        #     if form.is_valid():  # если пользователь ввёл всё правильно и нигде не накосячил, то сохраняем новый товар
        #         form.save()
        #     return redirect('privatelist')


            # responseUser = request.POST.get('responseUser_id')
            # print(responseUser)
            # replied_to_user = responseUser
            #
            # reply_text = request.POST.get('text')
            # print(reply_text)
            # if form.is_valid():
            #     form.save()
            # # new_reply = Reply.objects.create(
            # #
            # #     user=request.user,
            # #     text=reply_text,
            # #     replied_to_user=replied_to_user,
            # # )
            # subject = 'Новый ответ на ваш отклик'
            # message = f'Пользователь {request.user.username} оставил ответ на ваш отклик.'
            # from_email = 'managernewssk@mail.ru'
            # recipient_list = [request.replied_to_user.email]
            #
            # send_mail(subject, message, from_email, recipient_list)
            #
            # # Перенаправляем пользователя обратно на страницу откликов
            # return redirect('privatelist')

class ReplyList(ListView):
    model = Reply
    template_name = 'private_response.html'
    context_object_name = 'response_rep'







class DeleteResponseView(DeleteView):
    model = Response
    template_name = 'response_delete.html'  # Создайте шаблон подтверждения удаления
    success_url = reverse_lazy('privatelist')

class CategoryView(DetailView):
    model = Category
    template_name = 'category.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context['category'] = Category.objects.get(pk=self.kwargs['pk'])
        context['subscribers'] = category.subscribers.all()
        context['posts_sub'] = category.post_set.all()
        return context


@login_required


def subscribe_from_category(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.add(request.user.id)
    return redirect(request.META.get('HTTP_REFERER'))


@login_required

def unsubscribe_from_category(request, pk):
    category = Сategory.objects.get(pk=pk)
    category.subscribers.remove(request.user.id)
    return redirect(request.META.get('HTTP_REFERER'))

class SearchList(ListView):
    model = Response
    template_name = 'search.html'
    context_object_name = 'search'

    def get_queryset(self):
        user = self.request.user

        search_query = self.request.GET.get('search_query')
        if search_query:
            # Если есть поисковый запрос, фильтруем отклики
            return ResponseFilter(self.request.GET, queryset=Response.objects.filter(responseUser=user)).qs

    def get_context_data(self, **kwargs):
        user = self.request.user

        context = super().get_context_data(**kwargs)
        context['filter'] = ResponseFilter(self.request.GET, Response.objects.filter(responseUser=user))
        return context




    # @login_required
# def usial_login_view(request):
#     username = request.Post['username']
#     password = request.Post['password']
#     user = authenticate(self.request, username=username, password=password)
#     if user is not None:
#         OneTimeCode.objects.create(code=random.choice('abcde'), user=user)
#
# def login_with_code_view(request):
#     username = request.Post['username']
#     code = request.Post['code']
#     if OneTimeCode.objects.filters(code=code, user__name=username).exict():
#         login(request, user)


# Create your views here.
