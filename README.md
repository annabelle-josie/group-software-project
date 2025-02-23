# Down2Earth

This is the Down2Earth web application. This web application is a scrum-based Django project designed as an interactive sustainability game. Users create an account and log in to access a daily task system that encourages eco-friendly activities. Completing tasks and attending events earns them **leaves**, which can be used to purchase flowers for their personal garden, and points that are used for the leaderboard.

Coursework for ECM2434 at the University of Exeter

Group: Alvin and the MicroChipmunks

Members: Andy, Amy, Annabelle, David, James, Jason, Oliver

## **Key Features**

- **Challenges**: Users complete environmentally friendly challenges to earn rewards.
- **Personal Garden**: An empty garden that can be customized by purchasing flowers using leaf points.
- **Marketplace**: Users can unlock new plants and decorations using their earned points.
- **Leaderboard**: A ranking system that allows players to compare their sustainability efforts with others.
- **Events**: Users can attend real-world sustainability events to earn additional rewards.

The application uses multiple SQLite databases to store and manage data. The gamified approach encourages players to adopt sustainable habits while competing in a friendly, engaging way.

## Requirements

Before running the project, make sure you have the following installed:

- **Python 3.10+**  
- **pip**  
- **Virtual Environment (venv)**  
  *(Recommended for dependency management)*
- **SQLite**

## Setup Instructions

To run this Django-based web application locally, follow the steps below.

### How to Run the Project

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
python manage.py migrate
```

### 3. Run the Server

Still within the group-software-project folder start the server with the command:

```console
python manage.py runserver
```

A message should then appear saying: "Starting development server at http://127.0.0.1:8000/" this indicates the server is up and running, and the website is available to be accessed at the address http://127.0.0.1:8000/

## Navigating the website

Once running the website, you will be automatically directed to log in. You may either sign up with a new account or log in using an existing username from the list of test users below. You will not be able to access the rest of the site until you are logged in.

Once logged in you will be admitted to the home page. From here you can see your user's garden (this will by empty as a new user), your daily challenges and the option to scan a QR code.

As a new user you can earn leaves by completing challenges and attending events. You can see all active events in the events page, and the daily challenges from the homepage.

## Users available for development and testing

Three users of differing levels of access have been created to allow for easy testing and exploration of the site

1. Normal user -> Username: basicuser Password: easypeasy
2. Gamekeeper -> Username: gamekeeper1 Password: easypeasy

### Note to developers

When creating plants. No double quotes (") may be used. This will render the plant unclickable. Do not use them in facts, names or anything else. Instead use single quotes!
