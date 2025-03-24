# Down2Earth
This is the Down2Earth web application. This web application is a scrum-based Django project designed as an interactive sustainability game. Users create an account and log in to access a daily task system that encourages eco-friendly activities. Completing tasks and attending events earns them **leaves**, which can be used to purchase flowers for their personal garden, and points that are used for the leaderboard.

Group: Alvin and the MicroChipmunks

Members: Andy, Amy, Annabelle, David, James, Jason, Oliver

## **Key Features**

- **Challenges**: Users complete environmentally friendly that refresh daily challenges to earn rewards.
- **Personal Garden**: An empty garden that can be customized by purchasing flowers using leaf points.
- **Marketplace**: Users can unlock new plants and decorations using their earned points.
- **Leaderboard**: A ranking system that allows players to compare their sustainability efforts with others.
- **Events**: Users can attend real-world sustainability events to earn additional rewards. 
- **Achivements**: Users can see their achivements with a progress bar to see how close they are to completing it.
- **Friends**: Users can add another user as a friend with their username if they accept friend request they can compete on friends leaderboard and see their gardens. 

The application uses multiple SQLite databases to store and manage data. The gamified approach encourages players to adopt sustainable habits while competing in a friendly, engaging way.

## Requirements

Before running the project, make sure you have the following installed:

- **Python 3.10+**  
- **pip**  
- **Virtual Environment (venv)**  
  *(Recommended for dependency management)*
- **SQLite**

- To be able to use the reset password function if you get the code from git hub get the .env file from technical documents and add it to project root so that the App can access the SMTP infomation. 

## Setup Instructions

we deployed the website we used python anywhere 
To navigate to the deployed webpage go to web address

https://down2earth.eu.pythonanywhere.com/

To run this Django-based web application locally, follow the steps below.

### How to Run the Project Locally 

**Download the package from the repository**  
*(Ensure you have access to the latest version of the project.)*

### 1. Install Dependencies

Install the required dependencies listed in requirements.txt:

```console
pip install -r requirements.txt
```

### 2. Apply Migrations

Navigate to the group-software-project folder and set up the database schema:

```console
python manage.py makemigrations
```

```console
python manage.py migrate

```

### 3. create standard database
Still within the group-software-project folder create a standard database for the project with:

```console
python manage.py populate_database

```

### possible step instead of step 3 to create database modularly 

```console
python manage.py create_challenges

```

```console
python manage.py create_mock_users

```

```console
python manage.py create_achievements

```
```console
python manage.py create_mock_events

```
### 3. Run the Server

Still within the group-software-project folder start the server with the command:

```console
python manage.py runserver
```

A message should then appear saying: "Starting development server at http://127.0.0.1:8000/" this indicates the server is up and running, and the website is available to be accessed at the address http://127.0.0.1:8000/

## Navigating the website

Once running the website, you will be automatically directed to log in. You may either sign up with a new account or log in using an existing username from the list of test users below. You will not be able to access the rest of the site until you are logged in.

Once logged in you will be admitted to the home page. From here you can see your user's garden (this will by empty as a new user), your daily challenges which you can complete. You can also click to the edit garden button to edit the garden. 

You can navigate to the friends page to send and accept friends requests. 

You can go to the achievments page to see the progress for different achivements

As a new user you can earn leaves by completing challenges and attending events. You can see all active events in the events page, and the daily challenges from the homepage.

You can navigate to the market page to buy plants for your garden 

You can naviagte to the leaderboard to see the Highest 10 scores globally and the users own rank. 

You can scan QR codes to complete a Event or Challenge and this will take your User to that page. 


## Users available for development and testing

we have 6 users of differing levels of access have been created to allow for easy testing and exploration of the site

1. Normal user -> Username: Jason Password:password1
2. Normal user -> Username: Andy Password:password2 
3. Normal user -> Username: Annabelle Password: password3
4. Normal user-> Username: David Password: password4
5. Normal -> Username: Oliver  Password: password5
6. Admin -> Username: Amy Password: password6
7. Admin -> Usernamr: James Password: password7

All Admin are also Gamekeepers and an Admin can create a user and assign them to be a gamekeeper.
    
To run the Django tests, input the command:

```console
python manage.py test
```

### Note to developers

When creating plants. No double quotes (") may be used. This will render the plant unclickable. Do not use them in facts, names or anything else. Instead use single quotes!
