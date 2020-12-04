"""Access user  details from the database."""

import dataclasses
import enum
from typing import List, Optional

from saltapi.repository.database import database


class Permission(enum.Enum):
    """A permission."""

    SUBMIT_PROPOSAL = "SUBMIT_PROPOSAL"
    VIEW_PROPOSAL = "VIEW_PROPOSAL"

    @staticmethod
    def from_name(name: str) -> "Permission":
        """Return the permission for a name."""
        for _name, member in Permission.__members__.items():
            if _name == name:
                return member
        raise ValueError(f"Unknown permission: {name}")


class Role(enum.Enum):
    """A role."""

    ADMINISTRATOR = "ADMINISTRATOR"

    @staticmethod
    def from_name(name: str) -> "Role":
        """Return the permission for a name."""
        for _name, member in Role.__members__.items():
            if _name == name:
                return member
        raise ValueError(f"Unknown role: {name}")


class UserPermissions:
    """User permissions."""

    def __init__(self, user: "User") -> None:
        self.user = user

    async def submit_proposal(self, proposal_code: Optional[str]) -> bool:
        """Check whether the user can submit a proposal."""
        if not self.user.has_permission(Permission.SUBMIT_PROPOSAL):
            return False
        if not proposal_code:  # Is a new proposal
            return True
        if await self.user.has_role_of.pc(
            proposal_code
        ):  # User is a principal investigator
            return True
        if await self.user.has_role_of.pc(proposal_code):  # User is a principal contact
            return True
        return False


class UserRoles:
    """User roles."""

    def __init__(self, user: "User"):
        self.user = user

    async def pi(self, proposal_code: str) -> bool:
        """Check whether the user is a Principal Investigator."""
        return await _is_user_pi(self.user.username, proposal_code)

    async def pc(self, proposal_code: str) -> bool:
        """Check whether the user is a Principal Contact."""
        return await _is_user_pc(self.user.username, proposal_code)


@dataclasses.dataclass()
class User:
    """A SALT user."""

    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    roles: List[Role]
    permissions: List[Permission]

    def __post_init__(self) -> None:
        """Initialise roles abd permissions."""
        self.is_permitted_to = UserPermissions(self)
        self.has_role_of = UserRoles(self)

    def has_permission(self, permission: Permission) -> bool:
        """Check whether the user has a permission."""
        return permission in self.permissions

    def has_role(self, role: Role) -> bool:
        """Check whether the user has a role."""
        return role in self.roles


async def find_user_by_credentials(username: str, password: str) -> Optional[User]:
    """
    Find the user with a given username and password.

    In case the user credentials are invalid None is returned.

    Parameters
    ----------
    username : str
        The PIPT username.
    password : str
        The password of the user.

    Returns
    -------
    None.
    """
    query = """
SELECT PiptUser_Id
FROM PiptUser
WHERE Username=:username AND Password=MD5(:password)
    """
    values = {"username": username, "password": password}
    result = await database.fetch_one(query=query, values=values)
    if not result:
        return None
    return await find_user_by_id(result[0])


async def find_user_by_id(user_id: int) -> Optional[User]:
    """
    Find the user with a given user id.

    In case the user id does not exist None is returned.

    Parameters
    ----------
    user_id
        A PIPT user id.

    Returns
    -------
        The user.
    """
    sql = """
SELECT
    Username,
    FirstName,
    Surname,
    Email
FROM PiptUser AS u
    JOIN Investigator AS i using (Investigator_Id)
WHERE u.PiptUser_Id = :user_id
    """
    values = {"user_id": user_id}
    result = await database.fetch_one(query=sql, values=values)
    if not result:
        return None

    return User(
        id=user_id,
        username=result[0],
        first_name=result[1],
        last_name=result[2],
        email=result[3],
        roles=[],  # TODO: get user permissions
        permissions=[],  # TODO: get user permissions
    )


async def _is_user_pi(username: str, proposal_code: str) -> bool:
    """
    Check if the user is the Principal Investigator of a proposal.

    Parameters
    ----------
    username
        The PIPT username
    proposal_code
        The proposal code

    Returns
    -------
    True if the user is The Principal Investigator else False

    """
    query = """
SELECT Username FROM Proposal as p
    JOIN ProposalCode as pc ON p.ProposalCode_Id = pc.ProposalCode_Id
    JOIN ProposalContact as prc ON prc.ProposalCode_Id = pc.ProposalCode_Id
    JOIN PiptUser as pu ON pu.PiptUser_Id = prc.Leader_Id
WHERE Proposal_Code = :proposal_code
    """
    values = {"proposal_code": proposal_code}
    result = await database.fetch_one(query=query, values=values)
    if result and result[0] == username:
        return True
    return False


async def _is_user_pc(username: str, proposal_code: str) -> bool:
    """
    Check if the user is the Principal Contact of a proposal.

    Parameters
    ----------
    username
        The PIPT username
    proposal_code
        The proposal code

    Returns
    -------
    True if the user is the Principal Contact else False

    """
    query = """
SELECT Username FROM Proposal as p
    JOIN ProposalCode as pc ON p.ProposalCode_Id = pc.ProposalCode_Id
    JOIN ProposalContact as prc ON prc.ProposalCode_Id = pc.ProposalCode_Id
    JOIN PiptUser as pu ON pu.PiptUser_Id = prc.Contact_Id
WHERE Proposal_Code = :proposal_code
    """
    values = {"proposal_code": proposal_code}
    result = await database.fetch_one(query=query, values=values)
    if result and result[0] == username:
        return True
    return False
