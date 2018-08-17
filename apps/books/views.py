from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import *
import bcrypt

def index(request):
    return render(request, 'books/index.html')

def logout(request):
    request.session.clear()
    return redirect('/')

#render the form to add a new book
def add_book_page(request):
    if 'user_id' not in request.session:
        return redirect('/')
    return render(request, 'books/add_book.html', {'authors': Author.objects.all()})

#render the page for the list of books
def books(request):
    if 'user_id' not in request.session:
        return redirect('/')
    
    # get all the books
    books = Book.objects.all().order_by("-created_at")
    books_reviews = []
    for book in books:
        # get the review and the rating of this book
        review = Review.objects.filter(book_review=book)
        review = review[0]
        user = User.objects.get(my_reviews=review)
        books_reviews.append(
            {
                'id': book.id,
                'title': book.title,
                'rating': review.rating,
                'review': review.review,
                'reviewer_id': user.id,
                'reviewer_first_name': user.first_name,
                'review_created_at': review.created_at
            }
        )

    return render(request, 'books/books.html', {'books_reviews': books_reviews, 'range': range(5)})

#render the page for the list of books
def book_show(request, id):
    if 'user_id' not in request.session:
        return redirect('/')

    # get the book information
    book = Book.objects.get(id = id)

    # get the author of the book
    author = Author.objects.get(books = book)
    print('author:', author.name)

    # get the books reviews
    reviews = []
    r = Review.objects.filter(book_review = book)

    # get the reviewer name
    for review in r:
        u = User.objects.get(my_reviews=review)
        print('reviewer name:', u.first_name)

        reviews.append({
            'review': review.review,
            'rating': review.rating,
            'reviewer_id': u.id,
            'reviewer_first_name': u.first_name,
            'review_created_at': review.created_at
        })


    book_data = {
        'id': book.id,
        'title': book.title,
        'author': author.name,
        'reviews': reviews,
    }

    return render(request, 'books/book_show.html', {'book': book_data, 'range': range(5)})

#render the page for the list of books
def users_show(request, id):
    if 'user_id' not in request.session:
        return redirect('/')
    
    # get the user information
    u = User.objects.get(id = id)
    books = []
    # get the user reviews
    reviews = Review.objects.filter(reviewer=u)
    # print('reviews', len(reviews))

    for review in reviews:
        # get the book
        book = Book.objects.get(reviews=review)
        print('Book', book.title)

        books.append({
            'book_id': book.id,
            'book_title': book.title
        })

        user = {
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email,
            'alias': u.alias,
            'total_reviews': len(reviews),
            'books_reviews': books
        }

    return render(request, 'books/users_show.html', {'user': user})


############# Add Book #############
def add_book(request):
    if request.method != 'POST':
        return redirect('/')
    
    errors = Book.objects.basic_validator(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, key)

            # record form data to sessions
            request.session['title'] = request.POST['title']
            request.session['author'] = request.POST['author']
            request.session['review'] = request.POST['review']
        return redirect('/books/add')

    else:
        user = User.objects.get(id = request.session['user_id'])
        book = Book.objects
        author = Author.objects
        review = Review.objects

        # create the author
        if len(request.POST['author_list']) != 0:
            author.create(name=request.POST['author_list'])
        else:
            author.create(name=request.POST['author'])
        author = author.last()

        # create the book
        book.create(title=request.POST['title'], author=author)
        book = book.last()

        # create review
        review.create(review=request.POST['review'], rating=request.POST['rating'], reviewer=user, book_review=book)


        user_id = request.session['user_id']
        request.session.clear()
        request.session['user_id'] = user_id

        return redirect('/books')



def add_book_review(request):
    if request.method != 'POST':
        return redirect('/')

    # get the book object
    book = Book.objects.get(id = int(request.POST['id']))
    
    # get the user objects
    user = User.objects.get(id = request.session['user_id'])
    
    # create review
    review = Review.objects
    review.create(review=request.POST['review'], rating=request.POST['rating'], reviewer=user, book_review=book)
    return redirect('/books/'+request.POST['id'])
    
def login(request):
    if request.method != 'POST':
        messages.error(request, '*You must logged in first', 'login')
        return redirect('/')
    
    # no validation error so fetch the user data
    user = User.objects.filter(email = request.POST['email'])
    if not user: # if the user email doesn't exist redirect it back with error
        messages.error(request, '*Email or password is invalid', 'login')
        return redirect('/')

    user = user[0] # since it is a list, get the first element
    if not bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
        # password did not match so redirect the user back to fix the error
        messages.error(request, '*Email or password is invalid', 'login')
        return redirect('/')

    # password match so loggedthe user in 
    request.session['user_id'] = user.id
    return redirect('/books')


def register(request):
    #check if this a post request
    if request.method != 'POST':
        return redirect('/')
    
    errors = User.objects.basic_validator(request.POST)
    # check if any errors exist
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        
            # record form data to sessions
            request.session['first_name'] = request.POST['first_name']
            request.session['last_name'] = request.POST['last_name']
            request.session['email'] = request.POST['email']
            request.session['alias'] = request.POST['alias']

        return redirect('/')
    else:
        # check email already exist in the database
        user = User.objects.filter(email = request.POST['email'])
        if user:
            messages.error(request, '*Email already exist', 'email')
            request.session['first_name'] = request.POST['first_name']
            request.session['last_name'] = request.POST['last_name']
            request.session['email'] = request.POST['email']
            request.session['alias'] = request.POST['alias']
            return redirect('/')
        
        # Hash the user password first
        hash_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
        user = User.objects # create an object of the user table
        user.create(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            email = request.POST['email'],
            alias = request.POST['alias'],
            password = hash_pw
        )

    messages.success(request, 'You have successfull register', 'register')
    # New a user has been successfully register
    request.session.clear()
    request.session['user_id'] = user.last().id
    return redirect('/books')



