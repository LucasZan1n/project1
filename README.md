# Project 1

Web Programming with Python and JavaScript

In this project I made a website containing 5000 different books. There is a searchbar on the homepage where you can search by title, author, or the isbn of the book. This is not casesensitive and it works even with just a part of the title, author or isbn.

The books are imported from a csv file using a python script called "import.py". This script imports the books into the database.

When a search is requested, a list of all the matching books shows up. Within the book-containers the title, author, publication year and a "view" button are shown. When clicking on the "view" button you are being directed to a page of the book itself. This contains the title of the book, the author, the publication year and the isbn. Furthermore there is the average rating and the number of ratings given by the Good Reads API. Lastly reviews are shown if there are reviews written about the book. There is also a form where you can leave a review with the title, content and a rating from 1 to 5. Only registered users are able to leave a review.

Users register with username, email and password. The username and email need to be unique so users can't register twice. Once registered users are able to login and leave a review. Users only can leave one review for each book.

There is also an API which covers information about each book(/api/<isbn>). In here there is the title, author, publication year, isbn, number of reviews and average score of the book. The number of reviews and the average score are based on the reviews given on this webapp so this API and the API of Good Reads are not merged together.

There is a distinction between the templates. There are templates ending with (logged_in) and there are templates ending with (logged_out). I did this because this way the navbar could show if a user is logged in or not and the username would be displayed in the navbar.
