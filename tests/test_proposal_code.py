from zipfile import ZipFile
from io import BytesIO
from xml.etree import ElementTree
import zipfile


def create_zip():
    archive = BytesIO()
    with ZipFile(archive, 'w') as zip_file:
        with zip_file.open("Proposal.xml", "w") as proposal_file:
            proposal_file.write(b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
                                    <ns2:Proposal xmlns="http://www.salt.ac.za/PIPT/Proposal/Shared/2.7"
                                    xmlns:ns2="http://www.salt.ac.za/PIPT/Proposal/Phase2/4.8"
                                    xmlns:ns3="http://www.salt.ac.za/PIPT/Shared/1.4"
                                    xmlns:ns4="http://www.salt.ac.za/DataTransfer"
                                    xmlns:ns5="http://www.salt.ac.za/PIPT/BVIT/Phase1/1.0"
                                    xmlns:ns6="http://www.salt.ac.za/PIPT/BVIT/Phase2/1.6"
                                    xmlns:ns7="http://www.salt.ac.za/PIPT/Salticam/Phase1/1.5"
                                    xmlns:ns8="http://www.salt.ac.za/PIPT/Salticam/Phase2/1.9"
                                    xmlns:ns9="http://www.salt.ac.za/PIPT/RSS/Phase1/1.12"
                                    xmlns:ns10="http://www.salt.ac.za/PIPT/RSS/Phase2/2.3"
                                    xmlns:ns11="http://www.salt.ac.za/PIPT/RSS/Shared/1.11"
                                    xmlns:ns12="http://www.salt.ac.za/PIPT/HRS/Phase1/1.1"
                                    xmlns:ns13="http://www.salt.ac.za/PIPT/HRS/Phase2/1.7" code="2020-2-SCI-043"
                                    final="true"
                                    PrincipalInvestigator="ag@saao.ac.za"
                                    PrincipalContact="ag@saao.ac.za"></ns2:Proposal>''')
    return archive


zipped = ZipFile(create_zip(), "r")


def read_file():
    if "Proposal.xml" in zipped.namelist():
        file = zipped.open("Proposal.xml")
        tree = ElementTree.parse(file)
        proposal = tree.getroot()
        return proposal


def test_root_element_has_no_proposal_code():
    if 'code' not in read_file().attrib:
        raise ValueError("No proposal code supplied in the file Proposal.xml.")


def test_no_proposal_xml_file():
    if zipfile.is_zipfile(create_zip()) and "Proposal.xml" not in zipped.namelist():
        raise ValueError("The zipfile contains no file Proposal.xml.")


def test_file_is_zip_file():
    is_file_zipped = zipfile.is_zipfile(create_zip())
    if not is_file_zipped:
        raise ValueError("The file supplied is not a zip file")


def test_root_element_is_called_proposal():
    if not zipfile.is_zipfile(create_zip()) and read_file().tag != "Proposal":
        raise ValueError("The root element of your xml file is not called Proposal")


def test_proposal_code_available_and_valid():
    proposal_code = read_file().attrib['code']
    if zipfile.is_zipfile(create_zip()) and "code" in read_file().attrib:
        assert read_file().attrib["code"]

    elif proposal_code.startswith("Unsubmitted-") or proposal_code == "":
        assert None
    else:
        raise ValueError(f"Invalid proposal code: {proposal_code}.")


def test_no_proposal_code_on_root_element():
    if "code" not in read_file().attrib:
        raise ValueError("No proposal code supplied in the file Proposal.xml.")