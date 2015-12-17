MYBLOG PYTHON FLASK WEB APPLICATION
by Patrick Abejar


I. INTRODUCTION
The following web app programmed in Python uses Flask and SQLite3 to implement a
blog service that is capable of posting, editing, publishing, and categorizing
entries. It does this through 11 integral controllers that serve as an inter-
mediary between the database where these posts are stored and the web interface
where HTML templates are rendered. Data exists in the controllers in the form of
a Post object where information can be readily accessed and organized. The Post
object contains eight parameters in total. Seven of these parameters are metadata
such as the title, date published, author of the post, id of the post, last updated
date of the post, if the post is published, and the category the post belongs to.
The other parameter contains a string of the post itself. These eight parameters
also represent the eight columns in the database that belong to any given row, with
one row representing a Post. It is through these consistent representations of a
Post that one may have data freely flow from the database, to the controller, and
to the view with any tests or changes being performed on the database.


II. DIFFERENT ARRANGEMENTS OF POSTS 
    (controllers: /, /dashboard, /blogpost, /category)
There are four controllers that work to establish different views and perspectives
of the post stored in the database. For example, the / controller retrieves every
single post that is marked to be published from the database. Information such as
title, author, date posted, and date edited along with the post itself are passed
onto the HTML viewer. This is in contrast with the /dashboard controller which seeks
to pass on posts that only belong to the current user logged in. This is due to the
fact that the dashboard viewer allows for posts to be modified or deleted and only
the author of those posts should have that capability. The /blogpost controller
allows one post to be viewed at a time with a unique URL that acts as a permalink.
The /category controller allows posts that are characterized as published and of the
same category to be viewed on one page.

These controllers work in the same manner in that they utilize the same "SELECT data
FROM table WHERE specification" SQL statements to retrieve data with different inputs
named. Two of these controllers, /blogpost and /category, even share the same viewer to
display posts, specific_posts.html, and will both display no_post.html if no post with
the requested specification exists. The / controller has its own viewer at index.html
and /dashboard at dashboard.html. The different viewer is required of /dashboard as it
contains options that allow users to update their own post where the other viewers do
not.


III. LOGIN AND LOGOUT 
     (controllers: /login, /logout)
The /login and /logout controllers work by manipulating the data in cookies through
the session object available in Flask. /logout is an easy controller to manage as it
only requires that the username entry be popped. The /login controller accepts user
input data and checks it against a table in the database that contains usernames and
passwords. When this check passes, the user is popped on to the session object. For
this, a viewer is only necessary for /login as it needs this to accept user input.
/logout does not need user input or to display specific information.


IV. INSERT INTO TABLE 
    (controller: /post)
The /post controller is the only one that uses the "INSERT INTO TABLE" SQL statement
in order to add new posts to the database from an HTML viewer where users may input
information. The /post controller verifies that there is legitimate information that
was inputted by the user such as containing not only blank spaces or whitespaces. It
also works to refine the strings of title, category, and post to be placed in an SQL
statement in the event a user types in a single quotation character. This needs to be
escaped and a second quotation is added to escape it. Once data passed all this, it
will be placed in the database along with the associated timestamp information,
author, and given id. Automatically, the published option is turned on. Its location
in the database allows other controllers to view it as needed.


V. DELETE FROM TABLE 
   (controller: /delete)
The /delete controller receives information in order to determine what entry in the
database should be deleted. However, this information is not user inputted, rather it
is hidden and embedded in a separate form that encompasses a button reachable on the
dashboard viewer. Every post has a button and once clicked or touched, the ID number
of that post is sent to this /delete controller. It then will perform the "DELETE
FROM" SQL statement to remove that entry from the database, eliminating it from view
from any other controller.


VI. UPDATE 
    (controllers: /edit, /publish, /unpublish)
The /edit, /publish, and /unpublish controllers all interact in the same way with
the database in that they utilize the "UPDATE" SQL statement. The /edit SQL statement
takes in post title, post category, and the post itself as input in order replace pre-
existing post information. In order to make the editing process easier for users, the
/edit controller works in two parts. The first part works by receiving the post ID in
the same method that the /delete controller receives the post ID through the dashboard.
It also receives the post title, post category, and post itself from the database and
then prefills textboxes in an edit.html HTML viewer so that a user can begin where they
started off. The controller will then accept this information again in order to perform
the same checks and refining that exists in the /post controller. After all this is
passed and processed, the UPDATE is done on the database where other controllers are
able to view it as needed. That specific and same ID/ row in the database is updated.

The /publish and /unpublish controllers also retrieve ID information on the posts that
they wish to publish/unpublish in the same manner that the /delete controller does. Once
it has this ID information, then it can use the UPDATE statement to change the publish
entry in the database, where other controllers can view this as needed. There is a
function, generate_list_of_posts(), that forms the basis of the controllers in part II
that show pass posts to an HTML viewer to be shown in a specific manner requested. Based
on the specifications, the generate_list_of_posts() function may exclude posts that are
not marked as to be published, such as in the index.html and category viewers. In the
dashboard.html and permalink viewers, these unpublished posts are visible.


VII. REPEATED FUNCTIONS (logged_in(), generate_list_of_posts(), rtemplate())
In order to reduce the number of times the same lines are hard coded, these functions
serve as an easy way to repeat these same processes.

The logged_in() function is a simple function in that it uses the existence of the
'username' entry to determine if a user is logged in or not.

The generate_list_of_posts() function was explained in VI above. It gathers a list
from the database consistent with any specifications/conditions on the post data and
places that data in the form of a Post object in a list. This will help the rtemplate()
function explained below.

The rtemplate() function takes advantage of how many times the dashboard.html,
login.html, and other views are rendered and gathers all information in needs to pass
on to the HTML view. Often these HTML views require the same information, such as the
username, if posts exist, if logged in, and the list of posts from
generate_list_of_posts(), so this function works to gather all this data conveniently.
One is redirected to the login.html view when a user tries to access a controller that
they do not have access to when they are logged out. When a user improperly accesses a
controller while logged in (i.e. directly typing in http://127.0.0.1:5000/delete) they
will be sent back to their dashboard.html view. In both of these improper access
instances, the user has an error message displayed to them. There is an optional
parameter that allows this in the rtemplate() function and space on both dashboard.html
and login.html views to display such messages.


VIII. USERNAMES AND PASSWORDS
Username        Password
BarackObama     illinois
GeorgeBush      texas
BillClinton     arkansas
RonaldReagan    california
JimmyCarter     georgia