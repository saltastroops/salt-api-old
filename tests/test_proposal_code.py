from zipfile import ZipFile
from io import BytesIO
from saltapi.repository.proposal_repository import get_proposal_code
import pytest


def create_zip(xml: bytes, filename: str):
    archive = BytesIO()
    with ZipFile(archive, 'w') as zip_file:
        with zip_file.open(filename, "w") as proposal_file:
            proposal_file.write(xml)
    return archive


# testing to see if the the file 'Proposal.xml' has the proposal code attribute
def test_no_proposal_code():
    file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
          <Proposal  final="true">
          </Proposal>'''
    with pytest.raises(ValueError) as excinfo:
        get_proposal_code(create_zip(file, "Proposal.xml"))
    assert "No proposal code" in str(excinfo.value)


# testing to see if the zipped folder provided has a file named 'Proposal.xml'
def test_no_proposal_xml_file():
    file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
          <Proposal  code="2020-2-SCI-043" final="true">
          </Proposal>'''
    with pytest.raises(KeyError) as excinfo:
        get_proposal_code(create_zip(file, "file.xml"))
    assert "No file called Proposal.xml" in str(excinfo.value)


# testing to see if proposal code supplied in 'Proposal.xml' is valid
def test_valid_proposal_code():
    file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
          <Proposal  code="2020-2-SCI-043" final="true">
          </Proposal>'''
    assert get_proposal_code(create_zip(file, "Proposal.xml")) == "2020-2-SCI-043"


def test_proposal_code_is_unsubmitted():
    file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
          <Proposal  code="Unsubmitted-" final="true">
          </Proposal>'''
    assert get_proposal_code(create_zip(file, "Proposal.xml")) is None


# testing if the root element of the file 'Proposal.xml' is called 'Proposal'
def test_root_element_is_not_called_proposal():
    file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
          <Proposals  code="2020-2-SCI-043" final="true">
          </Proposals>'''
    with pytest.raises(ValueError) as excinfo:
        get_proposal_code(create_zip(file, "Proposal.xml"))
    assert "The root element in the file Proposal.xml" in str(excinfo.value)


@pytest.mark.parametrize("code", [("", None)])
def test_proposal_code_as_empty_string(code):
    file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
               <Proposal code="" final="true">
               </Proposal>'''
    assert get_proposal_code(create_zip(file, "Proposal.xml")) is None


@pytest.mark.parametrize("code, output", [("12", "Invalid proposal code: 12")])
def test_wrong_proposal_code(code, output):
    file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
               <Proposal code="12" final="true">
               </Proposal>'''
    with pytest.raises(ValueError):
        get_proposal_code(create_zip(file, "Proposal.xml"))
    assert "Invalid proposal code" in output


@pytest.mark.parametrize("code, output", [("submitted", "Invalid proposal code: submitted")])
def test_wrong_proposal_code_with_xml_namespace(code, output):
    file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
               <ns2:Proposal xmlns:ns2="http://www.salt.ac.za/PIPT/Proposal/Shared/2.7"
                code="submitted"></ns2:Proposal>'''
    with pytest.raises(ValueError):
        get_proposal_code(create_zip(file, "Proposal.xml"))
    assert "Invalid proposal code" in output


