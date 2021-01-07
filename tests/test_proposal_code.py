from zipfile import ZipFile
from io import BytesIO
from saltapi.repository.proposal_repository import get_proposal_code
import pytest


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


def zipfile_no_proposal_code():
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
                                    xmlns:ns13="http://www.salt.ac.za/PIPT/HRS/Phase2/1.7"
                                    final="true"
                                    PrincipalInvestigator="ag@saao.ac.za"
                                    PrincipalContact="ag@saao.ac.za"></ns2:Proposal>''')
    return archive


def zipfile_proposal_unsubmitted():
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
                                    xmlns:ns13="http://www.salt.ac.za/PIPT/HRS/Phase2/1.7" code="Unsubmitted-"
                                    final="true"
                                    PrincipalInvestigator="ag@saao.ac.za"
                                    PrincipalContact="ag@saao.ac.za"></ns2:Proposal>''')
    return archive


def zipfile_no_xml_file():
    archive = BytesIO()
    with ZipFile(archive, 'w') as zip_file:
        with zip_file.open("file.xml", "w") as proposal_file:
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


def zipfile_root_element_not_proposal():
    archive = BytesIO()
    with ZipFile(archive, 'w') as zip_file:
        with zip_file.open("Proposal.xml", "w") as proposal_file:
            proposal_file.write(b'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
                                    <ns2:Proposals xmlns="http://www.salt.ac.za/PIPT/Proposal/Shared/2.7"
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
                                    PrincipalContact="ag@saao.ac.za"></ns2:Proposals>''')
    return archive


def test_root_element_has_no_proposal_code():
    file = zipfile_no_proposal_code()
    with pytest.raises(ValueError) as execinfo:
        get_proposal_code(file)
    assert "No proposal code supplied in the file Proposal.xml." in str(execinfo.value)


def test_no_proposal_xml_file():
    file = zipfile_no_xml_file()
    with pytest.raises(KeyError) as execinfo:
        get_proposal_code(file)
    assert "There is no item named 'Proposal.xml' in the archive" in str(execinfo.value)


def test_no_proposal_code():
    file = zipfile_no_proposal_code()
    with pytest.raises(ValueError) as execinfo:
        get_proposal_code(file)
    assert "No proposal code supplied in the file Proposal.xml." in str(execinfo.value)


def test_valid_proposal_code():
    file = create_zip()
    assert get_proposal_code(file) == "2020-2-SCI-043"


def test_proposal_code_is_unsubmitted():
    file = zipfile_proposal_unsubmitted()
    assert get_proposal_code(file) is None


def test_root_element_is_called_proposal():
    file = zipfile_root_element_not_proposal()
    with pytest.raises(ValueError) as execinfo:
        get_proposal_code(file)
    assert "The root element of your xml file is not called Proposal" in str(execinfo.value)
