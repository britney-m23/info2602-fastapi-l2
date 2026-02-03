# import typer
# from app.database import create_db_and_tables, get_session, drop_all
# from app.models import User
# from fastapi import Depends
# from sqlmodel import or_, select
# from sqlalchemy.exc import IntegrityError

# cli = typer.Typer()

# @cli.command()
# def initialize():
    
    
    
#     with get_session() as db: # Get a connection to the database
#         drop_all() # delete all tables
#         create_db_and_tables() #recreate all tables
#         bob = User('bob', 'bob@mail.com', 'bobpass') # Create a new user (in memory)
#         db.add(bob) # Tell the database about this new data
#         db.commit() # Tell the database persist the data
#         db.refresh(bob) # Update the user (we use this to get the ID from the db)
#         print("Database Initialized")

# @cli.command()
# def get_user(username:str):
#      with get_session() as db: # Get a connection to the database
#         user = db.exec(select(User).where(User.username == username)).first()
#         if not user:
#             print(f'{username} not found!')
#             return
#         print(user)

# @cli.command()
# def get_all_users():
#     with get_session() as db:
#         all_users = db.exec(select(User)).all()
#         if not all_users:
#             print("No users found")
#         else:
#             for user in all_users:
#                 print(user)

# @cli.command()
# def change_email(username: str, new_email:str):
#    with get_session() as db: # Get a connection to the database
#         user = db.exec(select(User).where(User.username == username)).first()
#         if not user:
#             print(f'{username} not found! Unable to update email.')
#             return
#         user.email = new_email
#         db.add(user)
#         db.commit()
#         print(f"Updated {user.username}'s email to {user.email}")

# @cli.command()
# def create_user(username: str, email:str, password: str):
#     with get_session() as db: # Get a connection to the database
#         newuser = User(username, email, password)
#         try:
#             db.add(newuser)
#             db.commit()
#         except IntegrityError as e:
#             db.rollback() #let the database undo any previous steps of a transaction
#             #print(e.orig) #optionally print the error raised by the database
#             print("Username or email already taken!") #give the user a useful message
#         else:
#             print(newuser) # print the newly created user

# @cli.command()
# def delete_user(username: str):
#     with get_session() as db:
#         user = db.exec(select(User).where(User.username == username)).first()
#         if not user:
#             print(f'{username} not found! Unable to delete user.')
#             return
#         db.delete(user)
#         db.commit()
#         print(f'{username} deleted')

# @cli.command()
# def find_user(query: str):
#     with get_session() as db:
#         pattern = f"%{query}%"
#         users = db.exec(
#             select(User).where(
#                 or_(
#                     User.username.ilike(pattern),
#                     User.email.ilike(pattern)
#                 )
#             )
#         ).all()

#         if not users:
#             print(f"No users found matching '{query}'")
#             return

#         for user in users:
#             print(user)

# @cli.command()
# def list_users(limit: int = 10, offset: int = 0):
#     with get_session() as db:
#         users = db.exec(
#             select(User).offset(offset).limit(limit)
#         ).all()

#         for user in users:
#             print(user)

# if __name__ == "__main__":
#     cli()

import typer
from sqlmodel import select, or_
from sqlalchemy.exc import IntegrityError

from app.database import create_db_and_tables, get_session, drop_all
from app.models import User

cli = typer.Typer()


@cli.command()
def initialize():
    """
    Reset and initialize the database.

    This command:
    1) Drops all tables
    2) Recreates all tables
    3) Inserts a default sample user (bob)

    Useful for quickly resetting your database during development/testing.
    """
    with get_session() as db:
        drop_all()
        create_db_and_tables()

        bob = User("bob", "bob@mail.com", "bobpass")
        db.add(bob)
        db.commit()
        db.refresh(bob)

        print("Database Initialized")


@cli.command()
def get_user(
    username: str = typer.Argument(..., help="Exact username of the user to retrieve.")
):
    """
    Retrieve and print a single user by exact username.

    If no matching user is found, a not-found message is printed.
    """
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"{username} not found!")
            return
        print(user)


@cli.command()
def get_all_users():
    """
    Retrieve and print all users in the database.

    If there are no users, prints a message indicating the database is empty.
    """
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
            return

        for user in all_users:
            print(user)


@cli.command()
def change_email(
    username: str = typer.Argument(..., help="Exact username of the user to update."),
    new_email: str = typer.Argument(..., help="New email address to set for the user."),
):
    """
    Update a user's email address.

    Looks up the user by exact username. If found, updates their email and commits.
    If not found, prints an error message.
    """
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"{username} not found! Unable to update email.")
            return

        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")


@cli.command()
def create_user(
    username: str = typer.Argument(..., help="Username for the new user."),
    email: str = typer.Argument(..., help="Email address for the new user."),
    password: str = typer.Argument(..., help="Password for the new user."),
):
    """
    Create a new user.

    If the username or email is already taken (unique constraint), the transaction
    is rolled back and a user-friendly message is printed.
    """
    with get_session() as db:
        newuser = User(username, email, password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError:
            db.rollback()
            print("Username or email already taken!")
        else:
            print(newuser)


@cli.command()
def delete_user(
    username: str = typer.Argument(..., help="Exact username of the user to delete.")
):
    """
    Delete a user by exact username.

    If the user does not exist, prints an error message.
    """
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"{username} not found! Unable to delete user.")
            return

        db.delete(user)
        db.commit()
        print(f"{username} deleted")


@cli.command()
def find_user(
    query: str = typer.Argument(
        ...,
        help="Search text to partially match against username OR email (case-insensitive).",
    )
):
    """
    Find users by partial match of username OR email (case-insensitive).

    Returns all users where the username or email contains the given query text.
    """
    with get_session() as db:
        pattern = f"%{query}%"
        users = db.exec(
            select(User).where(
                or_(
                    User.username.ilike(pattern),
                    User.email.ilike(pattern),
                )
            )
        ).all()

        if not users:
            print(f"No users found matching '{query}'")
            return

        for user in users:
            print(user)


@cli.command()
def list_users(
    limit: int = typer.Argument(
        10, help="Maximum number of users to return (page size). Default is 10."
    ),
    offset: int = typer.Argument(
        0, help="Number of users to skip before returning results (page offset). Default is 0."
    ),
):
    """
    List users using limit/offset pagination.

    This is useful for paginated tables:
    - limit = page size
    - offset = how many rows to skip
    """
    with get_session() as db:
        users = db.exec(select(User).offset(offset).limit(limit)).all()
        for user in users:
            print(user)


if __name__ == "__main__":
    cli()
