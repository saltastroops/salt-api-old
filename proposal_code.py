from xml.etree import ElementTree
from zipfile import ZipFile


def get_proposal_code(proposal):
    archive = ZipFile(proposal, "r")
    file = archive.open("Proposal.xml")
    if not file:
        raise ValueError("There is no XML file containing the proposal code")
    tree = ElementTree.parse(file)
    root = tree.getroot()
    proposal_code = root.attrib['code']
    if proposal_code[0] != "2" or proposal_code.startswith("Unsubmitted-"):
        raise ValueError("Invalid proposal code")
    elif "Unsubmitted-" in proposal_code:
        return None
    return proposal_code
