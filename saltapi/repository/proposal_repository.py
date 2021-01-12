"""Access to proposal information."""

from typing import BinaryIO, Optional, Union
from defusedxml.ElementTree import parse
from zipfile import ZipFile
import zipfile


def get_proposal_code(proposal_zip: Union[str, BinaryIO]) -> Optional[str]:
    """Extract the proposal code from a proposal file."""
    if not zipfile.is_zipfile(proposal_zip):
        raise ValueError("The file supplied is not a zip file")

    try:
        archive = ZipFile(proposal_zip, "r")
        file = archive.open("Proposal.xml")
    except KeyError:
        raise KeyError("The zip file contains no file Proposal.xml.") from None

    tree = parse(file)
    proposal = tree.getroot()
    if "code" not in proposal.attrib:
        raise ValueError("No proposal code supplied in the file Proposal.xml.")

    if proposal.tag != "Proposal":
        raise ValueError("The root element in the file Proposal.xml is not called Proposal")

    proposal_code = proposal.attrib["code"]

    if proposal_code.startswith("2"):
        return proposal_code
    elif proposal_code.startswith("Unsubmitted-") or proposal_code == "":
        return None
    else:
        raise ValueError(f"Invalid proposal code: {proposal_code}.")


print(get_proposal_code("/home/lonwabolap/Downloads/Proposal.zip"))
