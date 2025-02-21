# group-software-project

Coursework for ECM2434

Group: Alvin and the MicroChipmunks
Members: Andy, Amy, Annabelle, David, James, Jason, Oliver

## Dependencies

It is assumed that the most recent version of Python (Python 3.13.2) is installed for this project. The following dependancies must also be installed

1. django
2. qrcode[PIL]

## How to run this project

There are two ways to run this project. Either through a python virtual environment or by the command line code

Command Line:
Inside the group-software-project directory type the following

```console
python manage.py runserver
```

A message should then appear saying: "Starting development server at http://127.0.0.1:8000/" this indicates the server is up and running, and the website is available to be accessed at the address http://127.0.0.1:8000/

## Navigating the website

Once running the website, you will be automatically directed to log in. You may either sign up with a new account or log in using an existing username from the list of test users below. You will not be able to access the rest of the site until you are logged in.

Once logged in you will be admitted to the home page. From here you can see your user's garden (this will consist of 6 sunflowers as placeholders if you are a new user), your daily challenges and the option to scan a QR code.

As a new user you are given a base amount of 50 leaves, which you can spend on plants in the market. You can earn more leaves by completing challenges and attending events. You can see all active events in the events page, and the daily challenges from the homepage.

## Users available for development and testing

Three users of differing levels of access have been created to allow for easy testing and exploration of the site

1. Normal user -> Username: basicuser Password: mypassword
2. Gamekeeper -> Username: gamekeeper1 Password: mypassword
3. Admin -> Do we need to give an admin password??

### Note to developers

When creating plants. No double quotes (") may be used. This will render the plant unclickable. Do not use them in facts, names or anything else. Instead use single quotes!
