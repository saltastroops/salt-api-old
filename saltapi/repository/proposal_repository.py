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
    except FileNotFoundError:
        raise KeyError("There is no item named 'Proposal.xml' in the archive") from None

    tree = ElementTree.parse(file)
    proposal = tree.getroot()
    if "code" not in proposal.attrib:
        raise ValueError("No proposal code supplied in the file Proposal.xml.")

    is_file_zipped = zipfile.is_zipfile(user_proposal)
    if not is_file_zipped:
        raise ValueError("The file supplied is not a zip file")

    if proposal.tag.split("}")[1] != "Proposal":
        raise ValueError("The root element of your xml file is not called Proposal")

    proposal_code = proposal.attrib["code"]

    if proposal_code.startswith("2"):
        return proposal_code
    elif proposal_code.startswith("Unsubmitted-") or proposal_code == "":
        return None
    else:
        raise ValueError(f"Invalid proposal code: {proposal_code}.")
