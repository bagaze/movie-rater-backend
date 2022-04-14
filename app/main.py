from fastapi import HTTPException
from pydantic import EmailStr
import uvicorn
import argparse
import asyncio

from app.schemas.user import UserCreate, UserInDB

from .app import app  # noqa: F401
from app.crud.users import UserCrud
from app.db.deps import DBSession


def __main__():
    ''' Run the application using `poetry run start` '''
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)


async def _create_super_admin(*, new_user: UserCreate) -> None:
    db_session = DBSession()
    await db_session.start()
    try:
        user_crud = UserCrud(db_session())
        await user_crud.create_new_user(
            new_user=new_user,
            is_superuser=True
        )
        print(f'New super user "{new_user.username}" successfully created')
    except HTTPException as e:
        print(f'Unable to create the new super user\nException: {str(e.detail)}')
    except Exception as e:
        print(f'Unable to create the new super user\nException: {str(e)}')
    finally:
        await db_session.stop()


def create_admin() -> UserInDB:
    ''' Create a new super admin using `poetry run create_admin` '''
    parser = argparse.ArgumentParser(description='Create new admin user.')
    parser.add_argument(
        'email',
        type=EmailStr,
        help='Email of the admin'
    )
    parser.add_argument(
        'username',
        type=str,
        help='Username of the admin'
    )
    parser.add_argument(
        'password',
        type=str,
        help='Password of the admin'
    )
    args = parser.parse_args()
    new_user = UserCreate(**vars(args))

    asyncio.run(_create_super_admin(new_user=new_user))
