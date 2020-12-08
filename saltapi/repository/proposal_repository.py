"""Access to proposal information."""

from typing import BinaryIO, Optional, Union
from xml.etree import ElementTree
from zipfile import ZipFile


def get_proposal_code(user_proposal: Union[str, BinaryIO]) -> Optional[str]:
    """Extract the proposal code from a proposal file."""
    try:
        archive = ZipFile(user_proposal, "r")
        file = archive.open("Proposal.xml")
    except FileNotFoundError:
        raise ValueError("The zipfile contains no file Proposal.xml.") from None

    tree = ElementTree.parse(file)
    proposal = tree.getroot()
    if "code" not in proposal.attrib:
        raise ValueError("No proposal code supplied in the file Proposal.xml.")

    proposal_code = proposal.attrib["code"]

    if proposal_code.startswith("2"):
        return proposal_code
    elif proposal_code.startswith("Unsubmitted-") or proposal_code == "":
        return None
    else:
        raise ValueError(f"Invalid proposal code: {proposal_code}.")
