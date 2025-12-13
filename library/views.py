from django.shortcuts import render, get_object_or_404
from .models import Book, Author, Review, Profile, ReviewVote
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect
from django.views.decorators.http import require_POST, require_http_methods
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .forms import ReviewForm

def home(request):
    last_viewed_ids = request.session.get('last_viewed_books', [])[:3]
    last_viewed_books = []
    if last_viewed_ids:
        preserved = models.Case(*[models.When(pk=pk, then=pos) for pos, pk in enumerate(last_viewed_ids)])
        last_viewed_books = list(Book.objects.filter(pk__in=last_viewed_ids).order_by(preserved))
    return render(request, "library/home.html", {"last_viewed_books": last_viewed_books})

def books(request):
    query = request.GET.get('q', '')
    if query:
        all_books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query)
        )
    else:
        all_books = Book.objects.all()
    return render(request, "library/books.html", {'books': all_books, 'query': query})

def authors(request):
    query = request.GET.get('q', '')
    if query:
        all_authors = Author.objects.filter(name__icontains=query)
    else:
        all_authors = Author.objects.all()
    return render(request, "library/authors.html", {'authors': all_authors, 'query': query})

def author_detail(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    books = author.books.all()
    return render(request, "library/author_detail.html", {'author': author, 'books': books})

def reviews(request):
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'latest')
    all_reviews = Review.objects.all()
    if query:
        all_reviews = all_reviews.filter(
            Q(book__title__icontains=query) |
            Q(book__author__name__icontains=query) |
            Q(review_text__icontains=query)
        )
    if sort == 'popular':
        all_reviews = all_reviews.order_by('-like_count', '-dislike_count', '-created_at')
    else:  # latest
        all_reviews = all_reviews.order_by('-created_at')
    user_votes = {}
    if request.user.is_authenticated:
        votes = ReviewVote.objects.filter(
            review__in=all_reviews,
            user=request.user
        )
        user_votes = {vote.review_id: vote.vote_type for vote in votes}
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'library/reviews_list.html', {
            'reviews': all_reviews,
            'user_votes': user_votes
        })
    return render(request, "library/reviews.html", {
        'reviews': all_reviews,
        'query': query,
        'user_votes': user_votes
    })

def news(request):
    return render(request, "library/news.html")

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'library/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'library/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def account(request):
    user = request.user
    all_users = None
    if user.is_authenticated:
        Profile.objects.get_or_create(user=user)
        if user.is_staff or user.is_superuser:
            all_users = User.objects.all()
    return render(request, "library/account.html", {"user": user, "all_users": all_users})

def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    # Track last viewed books in session
    last_viewed = request.session.get('last_viewed_books', [])
    if book_id in last_viewed:
        last_viewed.remove(book_id)
    last_viewed.insert(0, book_id)
    last_viewed = last_viewed[:3]  # Keep only the last 3
    request.session['last_viewed_books'] = last_viewed

    # Review filtering
    sort = request.GET.get('sort', 'date_desc')
    reviews = book.reviews.select_related('user').all()
    if sort == 'grade_asc':
        reviews = reviews.order_by('rating')
    elif sort == 'grade_desc':
        reviews = reviews.order_by('-rating')
    elif sort == 'date_asc':
        reviews = reviews.order_by('created_at')
    else:  # date_desc
        reviews = reviews.order_by('-created_at')

    # Review form logic
    review_form = None
    review_submitted = False
    if request.user.is_authenticated:
        if request.method == 'POST':
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.user = request.user
                review.book = book
                review.save()
                review_submitted = True
                review_form = ReviewForm()  # Reset form
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.template.loader import render_to_string
                    reviews = book.reviews.select_related('user').order_by('-created_at')
                    html = render_to_string('library/review_list_partial.html', {'reviews': reviews, 'user': request.user})
                    return JsonResponse({'success': True, 'html': html})
        else:
            review_form = ReviewForm()

    # Example bookshop links (customize as needed)
    bookshop_links = [
        {'name': 'Amazon', 'url': f'https://www.amazon.com/s?k={book.title.replace(" ", "+")}'},
        {'name': 'Book Depository', 'url': f'https://www.bookdepository.com/search?searchTerm={book.title.replace(" ", "+")}'},
    ]

    return render(request, 'library/book_detail.html', {
        'book': book,
        'author': book.author,
        'reviews': reviews,
        'sort': sort,
        'bookshop_links': bookshop_links,
        'review_form': review_form,
        'review_submitted': review_submitted,
    })

def books_ajax(request):
    query = request.GET.get('q', '')
    if query:
        all_books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query)
        )
    else:
        all_books = Book.objects.all()
    html = render_to_string('library/_book_list.html', {'books': all_books, 'user': request.user})
    return JsonResponse({'html': html})

@require_POST
def delete_user(request, user_id):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("You do not have permission to delete users.")
    if request.user.id == user_id:
        return HttpResponseForbidden("You cannot delete yourself.")
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(pk=user_id)
        user.delete()
    except User.DoesNotExist:
        pass
    return redirect('account')

def authors_ajax(request):
    query = request.GET.get('q', '')
    if query:
        all_authors = Author.objects.filter(name__icontains=query)
    else:
        all_authors = Author.objects.all()
    html = render_to_string('library/_author_list.html', {'authors': all_authors})
    return JsonResponse({'html': html})

@require_POST
@csrf_exempt
def like_review(request, review_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)
    review = Review.objects.get(pk=review_id)
    vote, created = ReviewVote.objects.get_or_create(user=request.user, review=review)
    if vote.vote_type == ReviewVote.LIKE:
        vote.delete()
    else:
        vote.vote_type = ReviewVote.LIKE
        vote.save()
    review.like_count = review.votes.filter(vote_type=ReviewVote.LIKE).count()
    review.dislike_count = review.votes.filter(vote_type=ReviewVote.DISLIKE).count()
    review.save()
    return JsonResponse({'like_count': review.like_count, 'dislike_count': review.dislike_count, 'user_vote': 'like' if vote.vote_type == ReviewVote.LIKE else None})

@require_POST
@csrf_exempt
def dislike_review(request, review_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)
    review = Review.objects.get(pk=review_id)
    vote, created = ReviewVote.objects.get_or_create(user=request.user, review=review)
    if vote.vote_type == ReviewVote.DISLIKE:
        vote.delete()
    else:
        vote.vote_type = ReviewVote.DISLIKE
        vote.save()
    review.like_count = review.votes.filter(vote_type=ReviewVote.LIKE).count()
    review.dislike_count = review.votes.filter(vote_type=ReviewVote.DISLIKE).count()
    review.save()
    return JsonResponse({'like_count': review.like_count, 'dislike_count': review.dislike_count, 'user_vote': 'dislike' if vote.vote_type == ReviewVote.DISLIKE else None})

@require_POST
def add_favorite(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)
    book_id = request.POST.get('book_id')
    if not book_id:
        return JsonResponse({'error': 'No book_id provided'}, status=400)
    try:
        book = Book.objects.get(pk=book_id)
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.favorites.add(book)
        return JsonResponse({'success': True, 'favorite': True})
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)

@require_POST
def remove_favorite(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)
    book_id = request.POST.get('book_id')
    if not book_id:
        return JsonResponse({'error': 'No book_id provided'}, status=400)
    try:
        book = Book.objects.get(pk=book_id)
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.favorites.remove(book)
        return JsonResponse({'success': True, 'favorite': False})
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)

@require_POST
def add_next_reading(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)
    book_id = request.POST.get('book_id')
    if not book_id:
        return JsonResponse({'error': 'No book_id provided'}, status=400)
    try:
        book = Book.objects.get(pk=book_id)
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.next_reading.add(book)
        return JsonResponse({'success': True, 'next_reading': True})
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)

@require_POST
def remove_next_reading(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)
    book_id = request.POST.get('book_id')
    if not book_id:
        return JsonResponse({'error': 'No book_id provided'}, status=400)
    try:
        book = Book.objects.get(pk=book_id)
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.next_reading.remove(book)
        return JsonResponse({'success': True, 'next_reading': False})
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)

@require_http_methods(["POST"])
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if review.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    book = review.book
    review.delete()
    # Return updated review list HTML
    reviews = book.reviews.select_related('user').order_by('-created_at')
    html = render_to_string('library/review_list_partial.html', {'reviews': reviews, 'user': request.user})
    return JsonResponse({'success': True, 'html': html})

@require_http_methods(["POST"])
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if review.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    form = ReviewForm(request.POST, instance=review)
    if form.is_valid():
        form.save()
        book = review.book
        reviews = book.reviews.select_related('user').order_by('-created_at')
        html = render_to_string('library/review_list_partial.html', {'reviews': reviews, 'user': request.user})
        return JsonResponse({'success': True, 'html': html})
    else:
        return JsonResponse({'error': 'Invalid form', 'form_errors': form.errors}, status=400)
