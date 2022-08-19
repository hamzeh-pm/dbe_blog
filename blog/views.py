from typing import Optional

from django.contrib.postgres.search import SearchVector
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from taggit.models import Tag

from .forms import CommentForm, EmailPostForm
from .models import Comment, Post


def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, "blog/post/list.html", {"posts": posts, "page": page})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status="published")
    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_post = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    print(similar_post)
    similar_post = similar_post.annotate(same_tags=Count("tags")).order_by(
        "-same_tags", "-publish"
    )[:4]

    # list of active comment
    comments = Comment.objects.filter(active=True)
    new_comment = None

    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "new_comment": new_comment,
            "comment_form": comment_form,
            "similar_post": similar_post,
        },
    )


class PostList(ListView):
    queryset = Post.published.all()
    paginate_by: int = 3
    context_object_name: Optional[str] = "posts"
    template_name: str = "blog/post/list.html"

    def get_queryset(self):
        tag_slug = self.kwargs.get("tag_slug")
        search_phrase = self.request.GET.get("search")
        print(search_phrase)
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            return super().get_queryset().filter(tags__in=[tag])

        if search_phrase:
            return (
                super()
                .get_queryset()
                .annotate(search_vector=SearchVector("title", "body"))
                .filter(search_vector=search_phrase)
            )

        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag_list"] = Tag.objects.all()

        tag_slug = self.kwargs.get("tag_slug")
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            context["tag"] = tag

        return context


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status="published")
    sent = False

    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # send email here
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url} \n\n {cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, "admin@myblog.com", [cd["to"]])
            sent = True
    else:
        form = EmailPostForm()

    return render(
        request, "blog/post/share.html", {"post": post, "form": form, "send": sent}
    )
