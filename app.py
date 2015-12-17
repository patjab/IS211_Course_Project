from flask import Flask
from flask import session
from flask import redirect
from flask import request
from flask import render_template
import sqlite3
import time
import re

__author__ = "Patrick Abejar"
app = Flask(__name__)


class Post:
    """Creates an object to easily organize and access posts by its
    components. Data pulled from the database is usually held in this
    Post object prior to being rendered as an HTML template."""
    def __init__(self, title, date, author, post, id, last_update,
                 is_published, category):
        self.title = title
        self.date = date
        self.author = author
        self.post = post
        self.id = id
        self.last_update = last_update
        self.is_published = is_published
        self.category = category


def logged_in():
    """Determines if a user is logged in or not. Mainly used for preventing
    users from viewing privileged pages and displaying if somebody is logged
    in or not."""
    if 'username' in session:
        return True
    else:
        return False


def generate_list_of_posts(selection=""):
    """Generates a list of posts to be published based on the data present in
    the database or a list of posts based on the user as entered in the para-
    meter. This function will also order that list by descending ID, meaning
    posted date in reverse chronological order.

    :param selection: filters the list received from the database based on
    the username in this parameter
    :return: returns a current list of posts by the criteria specified above
    """

    list_of_posts = []
    conn = sqlite3.connect("myblog.db")

    # Gets list for public view
    if selection == "":
        post_list = conn.execute("SELECT * FROM Posts WHERE is_published"
                                 " = 'YES' ORDER BY id DESC").fetchall()
    # Gets list for dashboard
    else:
        post_list = conn.execute("SELECT * FROM Posts WHERE username = '%s'"
                                 " ORDER BY id DESC" % selection).fetchall()

    for post in post_list:
        # Data gathered from the database is stored as follows in a list:
        input_id = post[0]
        input_title = post[1]
        input_username = post[2]
        input_date = post[3]
        input_last_update = post[4]
        input_post = post[5]
        input_is_published = post[6]
        input_category = post[7]

        # Placed in a Post object for easy access by the HTML template rendered
        list_of_posts.append(Post(input_title, input_date, input_username,
                                  input_post, input_id, input_last_update,
                                  input_is_published, input_category))
    conn.commit()
    conn.close()

    return list_of_posts


def rtemplate(page, message=""):
    """Gathers posts, username, login, status messages, and other data that is
    to be passed to the public view, dashboard, or login page. There are num-
    erous times that this information must be gathered and passed to the temp-
    late so that this function is to avoid repeated hard coding.

    :param page: HTML template to be rendered
    :param message: success or error message to be displayed on page rendered
    :return: renders page
    """
    # Generate list_of_posts based on the page desired and logged in status
    if logged_in():
        # Must display all posts with no filter for username for index.html
        if page == 'index.html':
            list_of_posts = generate_list_of_posts()
        else:
            list_of_posts = generate_list_of_posts(session['username'])
        username = session['username']
    else:
        list_of_posts = generate_list_of_posts()
        username = "Not Logged In"

    # Passes has_posts to the HTML template to determine if a no posts message
    # should be displayed
    has_posts = True
    if len(list_of_posts) == 0:
        has_posts = False

    return render_template(page, username=username, has_posts=has_posts,
                           logged_in=logged_in(), status_message=message,
                           list_of_posts=list_of_posts)


@app.route('/')
def index():
    """Displays the complete list of published posts regardless of logged in
    status through the rtemplate() function."""

    return rtemplate('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """HTML rendered template contains a form that prompts users who have not
    logged according to cookies to log in. Checks are done in order to verify
    that the inputted username and password exists in combination stored in
    the database. Status messages are displayed in the case of a login failure
    to the HTML template viewer. This is the controller users are directed to
    if at any time cookies fail to indicate a valid user."""

    # If the user is logged in they are sent to the dashboard with an error
    # message
    if logged_in():
        return rtemplate('dashboard.html', "ERROR: You are already logged in.")

    status_message = ""
    credentials_filled = 'username' in request.form and \
                         'password' in request.form

    # Must check if credentials are not null, otherwise the boolean storage of
    # correct_credentials will throw an error
    if credentials_filled:
        conn = sqlite3.connect("myblog.db")

        # Retrieves password based on username and tests for match
        c = conn.execute('''SELECT password
                            FROM Users
                            WHERE username = '%s' '''
                         % request.form['username'])
        correct_password_intermediate = c.fetchone()
        correct_credentials = False
        if correct_password_intermediate != None:
            correct_password = correct_password_intermediate[0]
            correct_credentials = c != None and \
                                  request.form['password'] == correct_password

    # Goes to the dashboard if credentials are correct. If a wrong entry is
    # inputted, then an error message will be displayed.
    if credentials_filled and correct_credentials:
        # Adds username to cookies when valid credentials are present
        session['username'] = request.form['username']
        return redirect('/dashboard')
    elif credentials_filled and not correct_credentials:
        status_message = "ERROR: No password matches that username."
    # Below occurs when the login.html page was first accessed
    elif not credentials_filled:
        status_message = ""

    return rtemplate('login.html', status_message)


@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    """Generates a list of posts specific to the logged in user that those
    titles will be displayed on a page that allows the editing, deletion,
    and publishing/unpublishing of those posts. Additionally, the HTML page
    rendered allows for the adding of new posts."""

    # Prevents non-logged in users from accessing any further material
    if not logged_in():
        status_message = "ERROR: You must be logged in to access the " \
                         "dashboard!"
        return rtemplate('login.html', status_message)

    return rtemplate('dashboard.html')


@app.route('/post', methods=['GET','POST'])
def post():
    """Takes in user entered data from the add new post form on the dashboard
    page. This controller performs logic tests that checks entered titles, cat-
    egories, and posts have characters other than whitespaces and that they
    are not blank. Refines these fields to allow single quotations to be enter-
    ed into databases via SQL statements without crashing by adding the escape
    character via find and replace in the regular expression package. Once the
    logic tests and refining are passed and completed all data will be input-
    ed into the database along with the time of input and the automatic pub-
    lishing setting on."""

    # Prevents non-logged in users from accessing any further material
    if not logged_in():
        return rtemplate('login.html', "ERROR: You must be logged in to post.")

    # Improper direct access will have the user redirected to the dashboard
    if len(request.form) == 0:
        return rtemplate('dashboard.html', "ERROR: You must post from the dashboard.")

    title = request.form['title']
    username = request.form['username']
    post = request.form['post']
    category = request.form['category']

    # Allows quotations to be inserted into the SQL statement
    refined_title = re.sub("[']", "''", title)
    refined_post = re.sub("[']", "''", post)
    refined_category = re.sub("[']", "''", category)

    pattern = "[^\s]+"
    # Logical test in the IF clause to determine that there is content other
    # than blanks and whitespace in titles, category, and post
    if re.search(pattern, refined_title) and \
            re.search(pattern, refined_category) and \
            re.search(pattern, refined_post):
        conn = sqlite3.connect("myblog.db")

        # Timestamp to be associated and displayed on posts
        now = time.strftime('%H:%M%p %Z on %b %d, %Y')
        yes_published = "YES"

        # Once all tests are passed, data is added to the database
        add_statement = '''INSERT INTO Posts
                           (id, title, username, date, is_published, post,
                           category)
                           VALUES
                           (NULL, '%s', '%s', '%s', '%s', '%s', '%s')''' % \
                            (refined_title, username, now, yes_published,
                             refined_post, category)

        conn.execute(add_statement)
        conn.commit()
        conn.close()

        status_message = "Successfully posted!"
    else:
        status_message = "ERROR: You must enter a valid title, category, and" \
                         " post. Entry was not posted."

    return rtemplate('dashboard.html', status_message)


@app.route('/delete', methods=['GET','POST'])
def delete():
    """Deletes posts based on ID. These requests originate from the dashboard
    HTML page from a button transmitting the ID of the post."""

    # Prevents non-logged in users from accessing any further material
    if not logged_in():
        return rtemplate('login.html', "ERROR: You must be logged in to delete"
                                       " posts!")

    # Improper direct access will have the user redirected to the dashboard
    if len(request.form) == 0:
        return rtemplate('dashboard.html', "ERROR: You must delete from the dashboard.")

    conn = sqlite3.connect("myblog.db")
    conn.execute('''DELETE FROM Posts WHERE id = %s''' % request.form['id'])
    conn.commit()
    conn.close()

    # Passes has_posts to the HTML template to determine if a no posts message
    # should be displayed
    return rtemplate('dashboard.html', "Successfully deleted!")


@app.route('/edit', methods=['GET','POST'])
def edit():
    """Edits posts based on ID. These requests originate from the dashboard
    HTML page from a button transmitting the ID of the post. The first part of
    the controller focuses on retrieving the components of the post in quest-
    ion from the database to feed back to the edit HTML page that places the
    information in the textboxes for easy editing. That HTML page then feeds
    back information to this edit() controller and then performs the same log-
    ic tests and refining that adding posts do. Once these two processes pass
    and are completed then the database is edited with the new user inputted
    data via an SQL update statement."""

    # Prevents non-logged in users from accessing any further material
    if not logged_in():
        return rtemplate('login.html', "ERROR: You must be logged in to edit "
                                       "posts.")

    # Improper direct access will have the user redirected to the dashboard
    if len(request.form) == 0:
        return rtemplate('dashboard.html', "ERROR: You must edit from the "
                                           "dashboard.")

    # FIRST PART pulls data from database for post to be edited and that will
    # be sent back to the HTML template for editing
    if 'still_needs_input' in request.form:
        conn = sqlite3.connect("myblog.db")
        c = conn.execute('''SELECT * FROM Posts WHERE id = %s'''
                         % request.form['id']).fetchone()
        conn.commit()
        conn.close()

        # Data is arranged in a list originating from the database as follows:
        # Index -> Info: 0 -> id; 1 -> title; 2 -> username; 3 -> date;
        # 4 -> last_update; 5 -> post; 6 -> is_published; 7 -> category
        id = c[0]
        title = c[1]
        post = c[5]
        category = c[7]
        return render_template('edit.html', title=title, id=id, post=post,
                               category=category,
                               username=session['username'],
                               logged_in=logged_in())

    # SECOND PART that performs logic tests and refining begins here
    title = request.form['title']
    id = request.form['id']
    post = request.form['post']
    category = request.form['category']

    # Allows quotations to be inserted into the SQL statement
    refined_title = re.sub("[']", "''", title)
    refined_post = re.sub("[']", "''", post)
    refined_category = re.sub("[']", "''", category)

    pattern = "[^\s]+"
    # Logic tests that checks that titles, categories, and posts don't contain
    # only whitespaces or blanks.
    if re.search(pattern, refined_title) \
            and re.search(pattern, refined_category) \
            and re.search(pattern, refined_post):
        conn = sqlite3.connect("myblog.db")

        # Edit is given a a new timestamp for the last_update to be displayed
        # along with the original date posted on the page of posts.
        now = time.strftime('%H:%M%p %Z on %b %d, %Y')

        # Updates with new information and adds additional timestamp for update
        conn.execute('''UPDATE Posts
                        SET title='%s', post='%s', last_update='%s',
                        category='%s'
                        WHERE id=%s''' % (refined_title, refined_post,
                                          now, refined_category, id))
        conn.commit()
        conn.close()
        status_message = "Successfully edited!"
    else:
        status_message = "ERROR: You must enter a valid title, category, " \
                         "and post! Entry was not posted."

    return rtemplate('dashboard.html', status_message)


@app.route('/publish', methods=['GET','POST'])
def publish():
    """Changes the is_published entry in the database of the requested ID to
    YES. It indirectly allows for the ability for posts to be displayed to the
    public."""

    # Prevents non-logged in users from accessing any further material
    if not logged_in():
        return rtemplate('login.html', "ERROR: Only logged in users can "
                                       "publish posts.")

    # Improper direct access will have the user redirected to the dashboard
    if len(request.form) == 0:
        return rtemplate('dashboard.html', "ERROR: You must publish from the "
                                           "dashboard.")

    id = request.form['id']

    conn = sqlite3.connect("myblog.db")
    conn.execute('''UPDATE Posts
                    SET is_published='YES'
                    WHERE id='%s';''' % (id))
    conn.commit()
    conn.close()

    return rtemplate('dashboard.html', "Successfully published!")


@app.route('/unpublish', methods=['GET','POST'])
def unpublish():
    """Changes the is_published entry in the database of the requested ID to
    NO. It indirectly allows for the ability for posts to be hidden from the
    public."""

    # Prevents non-logged in users from accessing any further material
    if not logged_in():
        return rtemplate('login.html', "ERROR: Only logged in users can "
                                       "unpublish posts.")

    # Improper direct access will have the user redirected to the dashboard
    if len(request.form) == 0:
        return rtemplate('dashboard.html', "ERROR: You must unpublish from the"
                                           " dashboard.")

    id = request.form['id']

    conn = sqlite3.connect("myblog.db")
    conn.execute('''UPDATE Posts
                    SET is_published='NO'
                    WHERE id='%s';''' % (id))
    conn.commit()
    conn.close()

    return rtemplate('dashboard.html', "Successfully unpublished!")


@app.route('/blogpost/<id>', methods=['GET','POST'])
def blogpost(id):
    """Allows for each blog post to have its own unique URL aka permalink.
    This does this by using the unique ID number associated with the post in
    question, and gathers all the information from the database with reference
    to this ID. This will be displayed on an HTML template."""

    conn = sqlite3.connect("myblog.db")
    c = conn.execute('''SELECT * FROM Posts WHERE id = '%s';''' % id)
    post_contents = c.fetchone()

    username_current = "Not logged in"
    if logged_in():
        username_current = session['username']

    # If no posts matches the ID given then the no_posts.html page is rendered.
    if post_contents is None:
        return render_template('no_post.html', logged_in=logged_in(),
                               username=username_current)

    # Data gathered from the database is stored as follows in a list:
    id = post_contents[0]
    title = post_contents[1]
    username = post_contents[2]
    date = post_contents[3]
    last_updated = post_contents[4]
    post = post_contents[5]
    is_published = post_contents[6]
    category = post_contents[7]

    # Data is packed in a Post object and then list to remain consistent with
    # the specific_posts.html input variables.
    post_shown = Post(title, date, username, post, id, last_updated,
                      is_published, category)
    list_of_posts = [post_shown]

    return render_template('specific_posts.html', list_of_posts=list_of_posts,
                           logged_in=logged_in(), username=username_current,
                           purpose="blogpost")


@app.route('/category/<category>', methods=['GET','POST'])
def category(category):
    """Allows for specified category to have its own unique URL and to be con-
    veniently displayed on one page. This does this by using category in the
    database and retrieving only those posts in a list to be passed to an HTML
    template."""

    conn = sqlite3.connect("myblog.db")
    c = conn.execute('''SELECT *
                        FROM Posts
                        WHERE category='%s' AND is_published='YES'
                        ORDER BY id DESC;''' % category)
    list_of_posts = []

    # Username displayed as follows:
    username_current = "Not logged in"
    if logged_in():
        username_current = session['username']

    for post in c.fetchall():
        # Data gathered from the database is stored as follows in a list:
        input_id = post[0]
        input_title = post[1]
        input_username = post[2]
        input_date = post[3]
        input_last_updated = post[4]
        input_post = post[5]
        input_is_published = post[6]
        input_category = post[7]

        # Placed in a Post object for easy access by the HTML template rendered
        list_of_posts.append(Post(input_title, input_date, input_username,
                                  input_post, input_id, input_last_updated,
                                  input_is_published, input_category))

    # If no post matches the category then no_post.html is rendered.
    if len(list_of_posts) == 0:
        return render_template('no_post.html', logged_in=logged_in(),
                               username=username_current)

    return render_template('specific_posts.html', list_of_posts=list_of_posts,
                           logged_in=logged_in(), username=username_current,
                           purpose="category", category=category)


@app.route('/logout')
def logout():
    """Logs out users"""
    # Prevents non-logged in users from accessing any further material
    if not logged_in():
        return rtemplate('login.html', "ERROR: You are not logged in!")

    # Logs out by updating cookies through session object
    session.pop('username', None)
    return redirect('/')


if __name__ == "__main__":
    # RUNS ON PORT 5000 ON 127.0.0.1, SINCE PORT 80 REQUIRES SUDO
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run()
