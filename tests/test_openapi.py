from pathlib import Path

from django.core.management import call_command


def test_openapi_schema_is_up_to_date(tmp_path):
    generated = tmp_path / "schema.yml"

    call_command("spectacular", "--file", str(generated))

    assert generated.read_text() == Path("schema.yml").read_text()
