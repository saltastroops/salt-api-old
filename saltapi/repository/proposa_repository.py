from xml.etree import ElementTree
from zipfile import ZipFile


def get_proposal_code(user_proposal: str):
    try:
        archive = ZipFile(user_proposal, "r")
        file = archive.open("Proposal.xml")
    except FileNotFoundError:
        raise ValueError("The zipped folder contains no file"
                         " called Proposal.xml") from None

    tree = ElementTree.parse(file)
    proposal = tree.getroot()
    if "code" not in proposal.attrib:
        raise ValueError("Proposal code is not supplied in the file Proposal.xml")

    proposal_code = proposal.attrib['code']

    if proposal_code.startswith("2"):
        return proposal_code
    elif proposal_code.startswith("Unsubmitted-") or proposal_code == "":
        return None
    else:
        return ValueError("Invalid proposal code from the file"
                          " in zipped folder (Proposal.xml) ")
