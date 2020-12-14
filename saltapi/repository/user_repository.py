"""Access user  details from the database."""

import dataclasses
import enum
from typing import List, Optional, Set

from saltapi.repository.database import database


class GlobalPermission(enum.Enum):
    """A permission."""

    SUBMIT_ANY_PROPOSAL = "SUBMIT_ANY_PROPOSAL"
    VIEW_ANY_PROPOSAL = "VIEW_ANY_PROPOSAL"
    VIEW_ANY_USERS_DETAILS = "VIEW_ANY_USERS_DETAILS"
    UPDATE_ANY_USERS_DETAILS = "UPDATE_ANY_USERS_DETAILS"
    UPDATE_PERMISSIONS = "UPDATE_PERMISSIONS"

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
    ACTIVE_USER = "ACTIVE_USER"

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
        if (
                self.user.has_global_permission(GlobalPermission.SUBMIT_ANY_PROPOSAL)
                or not proposal_code  # Is a new proposal
                or await self.user.has_role_of.pi(proposal_code)  # User is a principal investigator
                or await self.user.has_role_of.pc(proposal_code)  # User is a principal contact
        ):
            return True
        return False

    async def view_proposal(self, proposal_code) -> bool:
        if (
                self.user.has_global_permission(GlobalPermission.VIEW_ANY_PROPOSAL)
                or _is_proposal_investigator(self.user, proposal_code)
        ):
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
        """Initialise roles and permissions."""
        self.is_permitted_to = UserPermissions(self)
        self.has_role_of = UserRoles(self)

    def has_global_permission(self, permission: GlobalPermission) -> bool:
        """Check whether the user has a permission."""
        return permission in self.permissions

    def has_global_role(self, role: GlobalRole) -> bool:
        """Check whether the user has a role."""
        return role in self.roles


async def find_user_roles(user_id: int) -> Set[GlobalRole]:
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
SELECT PiptSetting_Name, `Value`, Active
FROM PiptUserSetting as pus
    JOIN PiptSetting as ps ON ps.PiptSetting_Id = pus.PiptSetting_Id
    JOIN PiptUser as pu ON pu.PiptUser_Id = pus.PiptUser_Id
WHERE pus.PiptUser_Id = :user_id
        """
    values = {"user_id": user_id}
    results = await database.fetch_all(query=query, values=values)
    user_roles: Set[GlobalRole] = set()
    if results:
        if results[0][2] == 1:
            user_roles.add(GlobalRole.ACTIVE_USER)
        else:
            return user_roles
        for row in results:
            if row[0] == "RightAdmin" and row[1] == 2:
                user_roles.add(GlobalRole.ADMINISTRATOR)
            if row[0] == "RightAstronomer" and row[1] == 1:
                user_roles.add(GlobalRole.SALT_ASTRONOMER)
            if row[0] == "RightOperator" and row[1] == 1:
                user_roles.add(GlobalRole.SALT_OPERATOR)
    return user_roles


async def find_user_permissions(user_id: int) -> Set[GlobalPermission]:
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

    user_roles = await find_user_roles(user_id=user_id)

    user_permissions: Set[GlobalPermission] = set()

    if GlobalRole.ADMINISTRATOR in user_roles:
        admin_defaults = {
            GlobalPermission.VIEW_ANY_PROPOSAL,
            GlobalPermission.SUBMIT_ANY_PROPOSAL,
            GlobalPermission.UPDATE_PERMISSIONS,
            GlobalPermission.VIEW_ANY_USERS_DETAILS,
            GlobalPermission.UPDATE_ANY_USERS_DETAILS}
        user_permissions.union(admin_defaults)

    if GlobalRole.SALT_ASTRONOMER in user_roles:
        sa_defaults = {
            GlobalPermission.VIEW_ANY_PROPOSAL,
            GlobalPermission.SUBMIT_ANY_PROPOSAL,
            GlobalPermission.VIEW_ANY_USERS_DETAILS}
        user_permissions.union(sa_defaults)

    if GlobalRole.SALT_OPERATOR in user_roles:
        so_defaults = {GlobalPermission.VIEW_ANY_PROPOSAL}
        user_permissions.union(so_defaults)

    return user_permissions


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
        roles=await find_user_roles(user_id),
        permissions=await find_user_permissions(user_id)
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
SELECT COUNT(Username) FROM  ProposalCode AS pc
    JOIN ProposalContact AS prc ON prc.ProposalCode_Id = pc.ProposalCode_Id
    JOIN Investigator AS i ON i.Investigator_Id = prc.Leader_Id
    JOIN PiptUser AS pu ON pu.PiptUser_Id = i.PiptUser_Id
WHERE Proposal_Code = :proposal_code
    AND Username = :username
    """
    values = {"proposal_code": proposal_code, "username": username}
    result = await database.fetch_one(query=query, values=values)
    if result and result[0] == 1:
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
SELECT COUNT(Username) FROM  ProposalCode AS pc
    JOIN ProposalContact AS prc ON prc.ProposalCode_Id = pc.ProposalCode_Id
    JOIN Investigator AS i ON i.Investigator_Id = prc.Contact_Id
    JOIN PiptUser AS pu ON pu.PiptUser_Id = i.PiptUser_Id
WHERE Proposal_Code = :proposal_code
    AND Username = :username
    """
    values = {"proposal_code": proposal_code}
    result = await database.fetch_one(query=query, values=values)
    if result and result[0] == 1:
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
SELECT COUNT(Username) FROM PiptUser pu
    JOIN Investigator i On pu.PiptUser_Id = i.PiptUser_Id
    JOIN ProposalInvestigator pi ON i.Investigator_Id = pi.Investigator_Id
    JOIN ProposalCode pc ON pi.ProposalCode_Id = pc.ProposalCode_Id
WHERE Username = :username AND Proposal_Code = :proposal_code
    """
    values = {"proposal_code": proposal_code, "username": user.username}
    result = await database.fetch_one(query=query, values=values)
    if result and result[0] == 1:
        return True
    return False
