"""Access to proposal information."""

from typing import BinaryIO, Optional, Union
from xml.etree import ElementTree
from zipfile import ZipFile
import zipfile


def get_proposal_code(user_proposal: Union[str, BinaryIO]) -> Optional[str]:
    """Extract the proposal code from a proposal file."""
    try:
        archive = ZipFile(user_proposal, "r")
        file = archive.open("Proposal.xml")
    except KeyError:
        raise KeyError("No file called Proposal.xml was found") from None

    tree = ElementTree.parse(file)
    proposal = tree.getroot()
    if "code" not in proposal.attrib:
        raise ValueError("No proposal code supplied in the file Proposal.xml.")

    if not zipfile.is_zipfile(user_proposal):
        raise ValueError("The file supplied is not a zip file")

    if proposal.tag != "Proposal":
        raise ValueError("The root element in the file Proposal.xml is not called Proposal")

    proposal_code = proposal.attrib["code"]

    if proposal_code.startswith("2"):
        return proposal_code
    elif proposal_code.startswith("Unsubmitted-") or proposal_code == "":
        return None
    else:
        raise ValueError(f"Invalid proposal code: {proposal_code}.")
