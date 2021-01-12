"""Tests for extracting the proposal code."""

from io import BytesIO
from zipfile import ZipFile

import pytest

from saltapi.repository.proposal_repository import get_proposal_code


def create_zip(xml: bytes, filename: str = "Proposal.xml"):
    """Create a zip file for the given XML content."""
    archive = BytesIO()
    with ZipFile(archive, "w") as zip_file:
        with zip_file.open(filename, "w") as proposal_file:
            proposal_file.write(xml)
    return archive


def test_not_a_zip_file():
    """Raise an error if the supplied file is not a zip file."""
    with pytest.raises(ValueError) as excinfo:
        file = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
               <Proposal xmlns:ns2="http://www.salt.ac.za/PIPT/Proposal/Shared/2.7"
                         code="2020-2-SCI-043">
               </Proposal>"""
        get_proposal_code(BytesIO(file))
    assert "not a zip file" in str(excinfo.value)


def test_no_proposal_xml_file():
    """Raise an error if the zip file has no file named 'Proposal.xml'."""
    file = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
          <Proposal code="2020-2-SCI-043" final="true">
          </Proposal>"""
    with pytest.raises(KeyError) as excinfo:
        get_proposal_code(create_zip(file, "file.xml"))
    assert "no file Proposal.xml" in str(excinfo.value)


def test_root_element_is_not_called_proposal():
    """Raise an error if the root element is not called 'Proposal'."""
    file = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
          <Proposals code="2020-2-SCI-043" final="true">
          </Proposals>"""
    with pytest.raises(ValueError) as excinfo:
        get_proposal_code(create_zip(file))
    assert "The root element in the file Proposal.xml" in str(excinfo.value)


def test_no_proposal_code():
    """Raise an error if the root element doesn't have a code attribute."""
    file = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
          <Proposal final="true">
          </Proposal>"""
    with pytest.raises(ValueError) as excinfo:
        get_proposal_code(create_zip(file))
    assert "No proposal code" in str(excinfo.value)


@pytest.mark.parametrize("code", ["1000-SCI-1-20", "submitted", "invalid"])
def test_invalid_proposal_code(code):
    """Raise an error if the proposal code is invalid."""
    file = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
               <Proposal code="%b" final="true">
               </Proposal>""" % bytes(
        code, "utf-8"
    )
    with pytest.raises(ValueError) as excinfo:
        get_proposal_code(create_zip(file))
    assert "Invalid proposal code" in str(excinfo.value)


@pytest.mark.parametrize(
    "code", ["2", "2a", "2021", "2020-1-SCI-005", "2021-2-DDT-001"]
)
def test_valid_proposal_code(code):
    """Valid proposal codes are parsed correctly."""
    file = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
          <Proposal code="%b" final="true">
          </Proposal>""" % bytes(
        code, "utf-8"
    )
    assert get_proposal_code(create_zip(file)) == code


@pytest.mark.parametrize("code", ["", "Unsubmitted-", "Unsubmitted-001"])
def test_proposal_code_empty_or_unsubmitted(code):
    """'Unsubmitted-...' proposal codes and empty strings are parsed as  None."""
    file = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
          <Proposal code="%b" final="true">
          </Proposal>""" % bytes(
        code, "utf-8"
    )
    assert get_proposal_code(create_zip(file)) is None


def test_file_with_xml_namespace():
    """Namespaces are supported."""
    code = "2020-2-SCI-009"
    file = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
               <ns2:Proposal xmlns:ns2="http://www.salt.ac.za/PIPT/Proposal/Shared/2.7"
                code="%b"></ns2:Proposal>""" % bytes(
        code, "utf-8"
    )
    assert get_proposal_code(create_zip(file)) == code
