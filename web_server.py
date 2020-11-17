from starlette.applications import Starlette
from starlette.routing import Route
from auth.login import login_user


async def login(request):
    return login_user(request)


app = Starlette(debug=True, routes=[
    Route('/login', login, methods=['POST']),
])