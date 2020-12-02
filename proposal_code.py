from xml.etree import ElementTree
from zipfile import ZipFile


def get_proposal_code(proposal):
    try:
        archive = ZipFile(proposal, "r")
        file = archive.open("Proposal.xml")
    except FileNotFoundError:
        raise ValueError("The zipped folder contains no file"
                         " called Proposal.xml") from None

    tree = ElementTree.parse(file)
    root = tree.getroot()
    proposal_code = root.attrib['code']
    if "code" not in root.attrib:
        raise ValueError("Proposal code is not supplied in the file Proposal.xml")
    elif proposal_code.startswith("2"):
        return proposal_code
    elif proposal_code.startswith("Unsubmitted-") or proposal_code == "":
        return None
    else:
        return ValueError("Invalid proposal code from the file"
                          " in zipped folder (Proposal.xml) ")
