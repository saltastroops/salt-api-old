from xml.etree import ElementTree


def get_proposal_code(proposal):
    tree = ElementTree.parse(proposal)
    root = tree.getroot()
    proposal_code = root.attrib['code']
    return proposal_code
