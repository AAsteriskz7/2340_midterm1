from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from cart.models import Item
import json

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

def popularity_map(request):
    items = Item.objects.select_related('order__user__profile', 'movie').all()

    trending_data = {}
    for item in items:
        try:
            region = item.order.user.profile.region.lower() 
        except Exception:
            region = 'southeast'

        if region not in trending_data:
            trending_data[region] = {}

        movie_name = item.movie.name
        if movie_name not in trending_data[region]:
            trending_data[region][movie_name] = 0

        trending_data[region][movie_name] += item.quantity

    coords = {
        'northeast': [40.8781, -77.7996], 
        'southeast': [33.9169, -80.8964],             
        'midwest': [40.0417, -89.1965],             
        'southwest': [34.2744, -111.6602],             
        'west': [43.9336, -120.5583]
    }

    map_data=[]
    for region, movies_dict in trending_data.items():
        sorted_movies = sorted(movies_dict.items(), key=lambda x: x[1], reverse=True)
        top_movies =  sorted_movies[:3]

        movies_str =  ", ".join([f"{name} ({count} purchases)" for name, count in top_movies])

        lat, lng = coords.get(region, [0,0])

        if lat != 0:
            display_name = region.capitalize()

            map_data.append({
                'region': display_name,
                'lat': lat,
                'lng': lng,
                'trending': movies_str
            })
    map_data_json = json.dumps(map_data)
    return render(request, 'movies/popularity_map.html', {'map_data_json': map_data_json})