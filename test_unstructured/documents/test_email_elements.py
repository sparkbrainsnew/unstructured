from functools import partial
import pytest

from unstructured.cleaners.core import clean_prefix
from unstructured.cleaners.translate import translate_text
from unstructured.documents.email_elements import EmailElement, NoID, Name, Email, MetaData, ReceivedInfo, Attachment

class TestEmail(Email):
    pass

def test_text_id():
    name_element = Name(name="Example", text="hello there!")
    assert name_element.id == "c69509590d81db2f37f9d75480c8efed"


def test_element_defaults_to_blank_id():
    element = EmailElement()
    assert isinstance(element.id, NoID)


def test_text_element_apply_cleaners():
    name_element = Name(name="[2] Example docs", text="[1] A Textbook on Crocodile Habitats")

    name_element.apply(partial(clean_prefix, pattern=r"\[\d{1,2}\]"))
    assert str(name_element) == "Example docs: A Textbook on Crocodile Habitats"


def test_name_element_apply_multiple_cleaners():
    cleaners = [
        partial(clean_prefix, pattern=r"\[\d{1,2}\]"),
        partial(translate_text, target_lang="ru"),
    ]
    name_element = Name(
        name="[1] A Textbook on Crocodile Habitats", text="[1] A Textbook on Crocodile Habitats"
    )
    name_element.apply(*cleaners)
    assert (
        str(name_element)
        == "Учебник по крокодильным средам обитания: Учебник по крокодильным средам обитания"
    )


def test_apply_raises_if_func_does_not_produce_string():
    name_element = Name(name="Example docs", text="[1] A Textbook on Crocodile Habitats")
    with pytest.raises(ValueError):
        name_element.apply(lambda s: 1)


def test_email_class():
    meta_data = MetaData(name="MIME-Version", text="1.0")
    received_info = ReceivedInfo(name="ABCDEFG-000.ABC.guide", text="ba23::58b5:2236:45g2:88h2"),
    attachment = Attachment(name="Attachment", text="Dummy attachment")
    test_obj = TestEmail(meta_data=meta_data, received_info=received_info, attachments=[attachment])
    EXPECTED_EMAIL_CLASS_OUTPUT = f"""
        Recipient: {test_obj.recipient}
        Sender: {test_obj.sender}
        Subject: {test_obj.subject}

        Received Header Information:

        {test_obj.received_info}

        Meta Data From Header:

        {test_obj.meta_data}

        Body:

        {test_obj.body}

        Attachment:

        {[file.name for file in test_obj.attachment]}
        """
    assert EXPECTED_EMAIL_CLASS_OUTPUT.strip() == test_obj.__str__().strip()