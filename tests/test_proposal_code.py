from zipfile import ZipFile
from io import BytesIO
from saltapi.repository.proposal_repository import get_proposal_code
import pytest


def create_zip(xml: bytes, filename: str = "Proposal.xml"):
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
        get_proposal_code(create_zip(file))
    assert "No proposal code" in str(excinfo.value)


# testing to see if the zipped folder provided has a file named 'Proposal.xml'
def test_no_proposal_xml_file():
    file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
          <Proposal  code="2020-2-SCI-043" final="true">
          </Proposal>'''
    with pytest.raises(KeyError) as excinfo:
        get_proposal_code(create_zip(file, "file.xml"))
    assert "no file Proposal.xml" in str(excinfo.value)


# testing to see if proposal code supplied in 'Proposal.xml' is valid
def test_valid_proposal_code():
    file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
          <Proposal  code="2020-2-SCI-043" final="true">
          </Proposal>'''
    assert get_proposal_code(create_zip(file)) == "2020-2-SCI-043"


# testing to see that an empty proposal code and other invalid variations will not be accepted
@pytest.mark.parametrize("code", ["", "Unsubmitted-", "Unsubmitted-001"])
def test_proposal_code_empty_and_unsubmitted(code):
    file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
          <Proposal code="%b" final="true">
          </Proposal>''' % bytes(str(code), "utf-8")
    assert get_proposal_code(create_zip(file)) is None


# testing if the root element of the file 'Proposal.xml' is called 'Proposal'
def test_root_element_is_not_called_proposal():
    file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
          <Proposals  code="2020-2-SCI-043" final="true">
          </Proposals>'''
    with pytest.raises(ValueError) as excinfo:
        get_proposal_code(create_zip(file))
    assert "The root element in the file Proposal.xml" in str(excinfo.value)


# testing that we get "Invalid proposal code" when proposal code does not start with 2 and other variations
@pytest.mark.parametrize("code", [("1000-SCI-1-20", "submitted", "invalid")])
def test_invalid_proposal_code(code):
    file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
               <Proposal code="%b" final="true">
               </Proposal>''' % bytes(str(code), "utf-8")
    with pytest.raises(ValueError) as excinfo:
        get_proposal_code(create_zip(file))
    assert "Invalid proposal code" in str(excinfo.value)


# When xml has namespaces, the root element is not cleanly given back, it's got the namespaces which we don't need
# so we test that when xml has a namespace in the root element, we raise an exception'
@pytest.mark.parametrize("code", [("2020-2-SCI-043", "2016-1-SCI-019")])
def test_file_with_xml_namespace(code):
    file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
               <ns2:Proposal xmlns:ns2="http://www.salt.ac.za/PIPT/Proposal/Shared/2.7"
                code="%b"></ns2:Proposal>''' % bytes(str(code), "utf-8")
    with pytest.raises(ValueError) as excinfo:
        get_proposal_code(create_zip(file))
    assert "The root element in the file Proposal.xml" in str(excinfo.value)


# test that the folder supplied is a zipped folder otherwise raise exception
def test_proposal_xml_folder_is_zipped():
    with pytest.raises(ValueError) as excinfo:
        file = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
               <ns2:Proposal xmlns:ns2="http://www.salt.ac.za/PIPT/Proposal/Shared/2.7" code="2020-2-SCI-043">
               </ns2:Proposal>'''
        get_proposal_code(BytesIO(file))
    assert "not a zip file" in str(excinfo.value)
