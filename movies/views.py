from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.db.models import Sum, Count
from cart.models import Item
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie, reported=False)

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)
@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        review.reported = True
        review.save()
        # review.delete()
    return redirect('movies.show', id=id)

@staff_member_required
def admin_analytics(request):
    # --- Find the most purchased movie --- #
    most_purchased_movie = (Item.objects.values("movie_id", "movie__name").annotate(total_bought=Sum("quantity")).order_by("-total_bought").first())
    template_data = {}
    template_data["most_purchased"] = most_purchased_movie
    # --- Find the most reviewed movie --- #
    most_reviewed_movie = (Review.objects.filter(reported=False).values("movie_id", "movie__name").annotate(total_reviews=Count("id")).order_by("-total_reviews").first())
    template_data["most_reviewed"] = most_reviewed_movie
    return render(request, 'movies/AdminAnalytics.html', {'template_data': template_data})