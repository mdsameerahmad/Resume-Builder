from app.services.json_validator import JsonValidator


def test_repairs_trailing_commas_and_unquoted_keys():
    response = """```json
    {
      contact: {"full_name": "Jane Doe",},
      "links": {},
      "skills": [],
      "projects": [],
      "experience": [],
      "education": [],
    }
    ```"""

    data = JsonValidator().clean_json_response(response)

    assert data["contact"]["full_name"] == "Jane Doe"


def test_extracts_json_from_surrounding_text():
    response = 'Here is the result: {"contact": {}, "links": {}} Thank you.'

    data = JsonValidator().clean_json_response(response)

    assert data == {"contact": {}, "links": {}}
