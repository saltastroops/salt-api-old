"""Access user  details from the database."""

import dataclasses
import enum
from typing import List, Optional

from saltapi.repository.database import database


class GlobalPermission(enum.Enum):
    """A permission."""

    SUBMIT_PROPOSAL = "SUBMIT_PROPOSAL"
    SUBMIT_ANY_PROPOSAL = "SUBMIT_ANY_PROPOSAL"
    VIEW_PROPOSAL = "VIEW_PROPOSAL"
    VIEW_ANY_PROPOSAL = "VIEW_ANY_PROPOSAL"
    UPDATE_PROPOSAL = "UPDATE_PROPOSAL"
    UPDATE_ANY_PROPOSAL = "UPDATE_ANY_PROPOSAL"
    VIEW_USERS_DETAILS = "VIEW_USERS_DETAILS"
    UPDATE_USERS_DETAILS = "UPDATE_USERS_DETAILS"
    UPDATE_PERMISSIONS = "UPDATE_PERMISSIONS"
    CREATE_PERMISSIONS = "CREATE_PERMISSIONS"
    VIEW_PERMISSIONS = "VIEW_PERMISSIONS"

    @staticmethod
    def from_name(name: str) -> "GlobalPermission":
        """Return the permission for a name."""
        for _name, member in GlobalPermission.__members__.items():
            if _name == name:
                return member
        raise ValueError(f"Unknown permission: {name}")


class GlobalRole(enum.Enum):
    """A role."""

    ADMINISTRATOR = "ADMINISTRATOR"
    SALT_ASTRONOMER = "SALT_ASTRONOMER"
    SALT_OPERATOR = "SALT_OPERATOR"

    @staticmethod
    def from_name(name: str) -> "GlobalRole":
        """Return the permission for a name."""
        for _name, member in GlobalRole.__members__.items():
            if _name == name:
                return member
        raise ValueError(f"Unknown role: {name}")


class UserPermissions:
    """User permissions."""

    def __init__(self, user: "User") -> None:
        self.user = user

    async def submit_proposal(self, proposal_code: Optional[str]) -> bool:
        """Check whether the user can submit a proposal."""
        if self.user.has_permission(GlobalPermission.SUBMIT_ANY_PROPOSAL):
            return True
        if not proposal_code:  # Is a new proposal
            return True
        if await self.user.has_role_of.pi(
            proposal_code
        ):  # User is a principal investigator
            return True
        if await self.user.has_role_of.pc(proposal_code):  # User is a principal contact
            return True
        return False

    async def view_proposal(self, proposal_code) -> bool:
        if self.submit_proposal(proposal_code):
            return True
        if _is_proposal_investigator(self.user, proposal_code):
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
    roles: List[GlobalRole]
    permissions: List[GlobalPermission]

    def __post_init__(self) -> None:
        """Initialise roles abd permissions."""
        self.is_permitted_to = UserPermissions(self)
        self.has_role_of = UserRoles(self)

    def has_permission(self, permission: GlobalPermission) -> bool:
        """Check whether the user has a permission."""
        return permission in self.permissions

    def has_role(self, role: GlobalRole) -> bool:
        """Check whether the user has a role."""
        return role in self.roles


async def find_user_roles(user_id: int) -> List[GlobalRole]:
    """
    Check for the user roles.

    Parameters
    ----------
    user_id
        The PIPT user id

    Returns
    -------
    The user roles

    """
    query = """
SELECT PiptSetting_Id, `Value`
FROM PiptUserSetting
WHERE PiptUser_Id = :user_id
        """
    values = {"user_id": user_id}
    results = await database.fetch_all(query=query, values=values)
    user_roles: List[GlobalRole] = []
    if results:
        for row in results:
            if row[0] == 22 and row[1] == 2:
                user_roles.append(GlobalRole.ADMINISTRATOR)
            if row[0] == 21 and row[1] == 1:
                user_roles.append(GlobalRole.SALT_ASTRONOMER)
            if row[0] == 23 and row[1] == 1:
                user_roles.append(GlobalRole.SALT_OPERATOR)
    return user_roles


async def find_user_permissions(user_id: int) -> List[GlobalPermission]:
    """
    Check for the user permissions.

    Parameters
    ----------
    user_id
        The PIPT user id

    Returns
    -------
    The user permissions

    """
    query = """
    SELECT PiptSetting_Id, `Value`
    FROM PiptUserSetting
    WHERE PiptUser_Id = :user_id
            """
    values = {"user_id": user_id}
    results = await database.fetch_all(query=query, values=values)
    user_permissions = []
    if results:
        for row in results:
            if row[0] == 22 and row[1] == 2:
                admin_defaults = [
                    GlobalPermission.UPDATE_ANY_PROPOSAL,
                    GlobalPermission.VIEW_ANY_PROPOSAL,
                    GlobalPermission.SUBMIT_ANY_PROPOSAL,
                    GlobalPermission.VIEW_PERMISSIONS,
                    GlobalPermission.UPDATE_PERMISSIONS,
                    GlobalPermission.CREATE_PERMISSIONS,
                    GlobalPermission.VIEW_USERS_DETAILS,
                    GlobalPermission.UPDATE_USERS_DETAILS
                ]
                user_permissions += admin_defaults
            if row[0] == 21 and row[1] == 1:
                sa_defaults = [
                    GlobalPermission.UPDATE_ANY_PROPOSAL,
                    GlobalPermission.VIEW_ANY_PROPOSAL,
                    GlobalPermission.SUBMIT_ANY_PROPOSAL,
                    GlobalPermission.VIEW_USERS_DETAILS
                ]
                user_permissions += sa_defaults
            if row[0] == 23 and row[1] == 1:
                so_defaults = [
                    GlobalPermission.VIEW_ANY_PROPOSAL,
                    GlobalPermission.VIEW_USERS_DETAILS
                ]
                user_permissions += so_defaults
    return list(dict.fromkeys(user_permissions))


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
        roles=find_user_roles(user_id),  # TODO: get user permissions
        permissions=find_user_permissions(user_id),  # TODO: get user permissions
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


async def _is_proposal_investigator(user: User, proposal_code: str):
    """
    Check if the user is the investigator of a proposal.

    Parameters
    ----------
    user
        The PIPT user
    proposal_code
        The proposal code

    Returns
    -------
    True if the user is the Investigator of a proposal

    """
    query = """
SELECT Username FROM Proposal as p
    JOIN ProposalCode as pc ON p.ProposalCode_Id = pc.ProposalCode_Id
    JOIN ProposalInvestigator as pri ON pri.ProposalCode_Id = pc.ProposalCode_Id
    JOIN PiptUser as pu ON pu.PiptUser_Id = pri.Investigator_Id
WHERE Proposal_Code = :proposal_code
And p.Current = 1
    """
    values = {"proposal_code": proposal_code}
    results = await database.fetch_all(query=query, values=values)
    pis = []
    if results:
        pis = [row[0] for row in results]
    return user.username in pis
