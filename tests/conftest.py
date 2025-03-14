"""This module contains fixtures and other helpful functions for the tests."""

import copy
import filecmp
import itertools
import json
import pathlib
import shutil
import typing
import urllib.request
from typing import Optional

import jinja2
import pydantic
import pydantic_extra_types.phone_numbers as pydantic_phone_numbers
import pypdf
import pytest
import ruamel.yaml

from rendercv import data
from rendercv.renderer import templater

# RenderCV is being tested by comparing the output to reference files. Therefore,
# reference files should be updated when RenderCV is updated in a way that changes
# the output. Setting update_testdata to True will update the reference files with
# the latest RenderCV. This should be done with caution, as it will overwrite the
# reference files with the latest output.
update_testdata = False

education_entry_dictionary = {
    "institution": "Boğaziçi University",
    "location": "Istanbul, Turkey",
    "degree": "BS",
    "area": "Mechanical Engineering",
    "start_date": "2015-09",
    "end_date": "2020-06",
    "highlights": [
        "GPA: 3.24/4.00 ([Transcript](https://example.com))",
        "Awards: Dean's Honor List, Sportsperson of the Year",
    ],
}

experience_entry_dictionary = {
    "company": "Some Company",
    "location": "TX, USA",
    "position": "Software Engineer",
    "start_date": "2020-07",
    "end_date": "2021-08-12",
    "highlights": [
        (
            "Developed an [IOS application](https://example.com) that has received more"
            " than **100,000 downloads**."
        ),
        "Managed a team of **5** engineers.",
    ],
}

normal_entry_dictionary = {
    "name": "Some Project",
    "location": "Remote",
    "date": "2021-09",
    "highlights": [
        "Developed a web application with **React** and **Django**.",
        "Implemented a **RESTful API**",
    ],
}

publication_entry_dictionary = {
    "title": (
        "Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of"
        " No-Insulation Coils"
    ),
    "authors": ["J. Doe", "***H. Tom***", "S. Doe", "A. Andsurname"],
    "date": "2021-12-08",
    "journal": "IEEE Transactions on Applied Superconductivity",
    "doi": "10.1109/TASC.2023.3340648",
}

one_line_entry_dictionary = {
    "label": "Programming",
    "details": "Python, C++, JavaScript, MATLAB",
}

bullet_entry_dictionary = {
    "bullet": "This is a bullet entry.",
}

numbered_entry_dictionary = {
    "number": "This is a numbered entry.",
}

reversed_numbered_entry_dictionary = {
    "reversed_number": "This is a reversed numbered entry.",
}


@pytest.fixture
def publication_entry() -> dict[str, str | list[str]]:
    """Return a sample publication entry."""
    return copy.deepcopy(publication_entry_dictionary)


@pytest.fixture
def experience_entry() -> dict[str, str]:
    """Return a sample experience entry."""
    return copy.deepcopy(experience_entry_dictionary)


@pytest.fixture
def education_entry() -> dict[str, str]:
    """Return a sample education entry."""
    return copy.deepcopy(education_entry_dictionary)


@pytest.fixture
def normal_entry() -> dict[str, str]:
    """Return a sample normal entry."""
    return copy.deepcopy(normal_entry_dictionary)


@pytest.fixture
def one_line_entry() -> dict[str, str]:
    """Return a sample one line entry."""
    return copy.deepcopy(one_line_entry_dictionary)


@pytest.fixture
def bullet_entry() -> dict[str, str]:
    """Return a sample bullet entry."""
    return copy.deepcopy(bullet_entry_dictionary)


@pytest.fixture
def numbered_entry() -> dict[str, str]:
    """Return a sample numbered entry."""
    return copy.deepcopy(numbered_entry_dictionary)


@pytest.fixture
def reversed_numbered_entry() -> dict[str, str]:
    """Return a sample reversed numbered entry."""
    return copy.deepcopy(reversed_numbered_entry_dictionary)


@pytest.fixture
def text_entry() -> str:
    """Return a sample text entry."""
    return (
        "This is a *TextEntry*. It is only a text and can be useful for sections like"
        " **Summary**. To showcase the TextEntry completely, this sentence is added,"
        " but it doesn't contain any information."
    )


@pytest.fixture
def rendercv_data_model() -> data.RenderCVDataModel:
    """Return a sample RenderCV data model."""
    return data.create_a_sample_data_model()


@pytest.fixture
def rendercv_data_as_python_dictionary(
    rendercv_data_model,
) -> dict:
    """Return a sample RenderCV data as a Python dictionary."""
    data_model_as_json = rendercv_data_model.model_dump_json(
        exclude_none=False, by_alias=True, exclude={"cv": {"sections", "photo"}}
    )
    return json.loads(data_model_as_json)


@pytest.fixture
def rendercv_empty_curriculum_vitae_data_model() -> data.CurriculumVitae:
    """Return an empty CurriculumVitae data model."""
    return data.CurriculumVitae(sections={"test": ["test"]})


def return_a_value_for_a_field_type(
    field: str,
    field_type: typing.Any,
) -> str:
    """Return a value for a given field and field type.

    Example:
        ```python
        return_a_value_for_a_field_type("institution", str)
        ```
        returns
        `"Boğaziçi University"`

    Args:
        field_type: The type of the field.

    Returns:
        A value for the field.
    """
    field_dictionary = {
        "institution": "Boğaziçi University",
        "location": "Istanbul, Turkey",
        "degree": "BS",
        "area": "Mechanical Engineering",
        "start_date": "2015-09",
        "end_date": "2020-06",
        "date": "2021-09",
        "summary": (
            "Did *this* and this is a **bold** [link](https://example.com). But I must"
            " explain to you how all this mistaken idea of denouncing pleasure and"
            " praising pain was born and I will give you a complete account of the"
            " system, and expound the actual teachings of the great explorer of the"
            " truth, the master-builder of human happiness. No one rejects, dislikes,"
            " or avoids pleasure itself, because it is pleasure, but because those who"
            " do not know how to pursue pleasure rationally encounter consequences that"
            " are extremely painful."
        ),
        "highlights": [
            (
                "Did *this* and this is a **bold** [link](https://example.com). But I"
                " must explain to you how all this mistaken idea of denouncing pleasure"
                " and praising pain was born and I will give you a complete account of"
                " the system, and expound the actual teachings of the great explorer of"
                " the truth, the master-builder of human happiness. No one rejects,"
                " dislikes, or avoids pleasure itself, because it is pleasure, but"
                " because those who do not know how to pursue pleasure rationally"
                " encounter consequences that are extremely painful."
            ),
            (
                "Did that. Nor again is there anyone who loves or pursues or desires to"
                " obtain pain of itself, because it is pain, but because occasionally"
                " circumstances occur in which toil and pain can procure him some great"
                " pleasure."
            ),
        ],
        "company": "Some Company",
        "position": "Software Engineer",
        "name": "My Project",
        "label": "Pro**gram**ming",
        "details": "Python, C++, JavaScript, MATLAB",
        "authors": [
            "J. Doe",
            "***H. Tom***",
            "S. Doe",
            "A. Andsurname",
            "S. Doe",
            "A. Andsurname",
            "S. Doe",
            "A. Andsurname",
            "S. Doe",
            "A. Andsurname",
        ],
        "title": (
            "Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of"
            " No-Insulation Coils"
        ),
        "journal": "IEEE Transactions on Applied Superconductivity",
        "doi": "10.1007/978-3-319-69626-3_101-1",
        "url": "https://example.com",
    }

    field_type_dictionary = {
        pydantic.HttpUrl: "https://example.com",
        pydantic_phone_numbers.PhoneNumber: "+905419999999",
        str: (
            "Did *this* and this is a **bold** [link](https://example.com). But I must"
            " explain to you how all this mistaken idea of denouncing pleasure and"
            " praising pain was born and I will give you a complete account of the"
            " system, and expound the actual teachings of the great explorer of the"
            " truth, the master-builder of human happiness. No one rejects, dislikes,"
            " or avoids pleasure itself, because it is pleasure, but because those who"
            " do not know how to pursue pleasure rationally encounter consequences that"
            " are extremely painful."
        ),
        list[str]: ["A string", "Another string"],
        int: 1,
        float: 1.0,
        bool: True,
    }

    if field in field_dictionary:
        return field_dictionary[field]
    if type(None) in typing.get_args(field_type):
        return return_a_value_for_a_field_type(field, field_type.__args__[0])
    if typing.get_origin(field_type) == typing.Literal:
        return field_type.__args__[0]
    if typing.get_origin(field_type) == typing.Union:
        return return_a_value_for_a_field_type(field, field_type.__args__[0])
    if field_type in field_type_dictionary:
        return field_type_dictionary[field_type]

    return "A string"


def create_combinations_of_a_model(
    model: type[data.Entry],
) -> list[data.Entry]:
    """Look at the required fields and optional fields of a model and create all
    possible combinations of them.

    Args:
        model: The data model class to create combinations of.

    Returns:
        All possible instances of the model.
    """
    fields = typing.get_type_hints(model)

    required_fields = {}
    optional_fields = {}

    for field, field_type in fields.items():
        value = return_a_value_for_a_field_type(field, field_type)
        if type(None) in typing.get_args(field_type):  # check if a field is optional
            optional_fields[field] = value
        else:
            required_fields[field] = value

    model_with_only_required_fields = model(**required_fields)

    # create all possible combinations of optional fields
    all_combinations = [model_with_only_required_fields]
    for i in range(1, len(optional_fields) + 1):
        for combination in itertools.combinations(optional_fields, i):
            kwargs = {k: optional_fields[k] for k in combination}
            model_instance = copy.deepcopy(model_with_only_required_fields)
            model_instance.__dict__.update(kwargs)
            all_combinations.append(model_instance)

    return all_combinations


@pytest.fixture
def rendercv_filled_curriculum_vitae_data_model(
    text_entry, bullet_entry, testdata_directory_path
) -> data.CurriculumVitae:
    """Return a filled CurriculumVitae data model, where each section has all possible
    combinations of entry types.
    """
    profile_picture_path = testdata_directory_path / "profile_picture.jpg"
    if update_testdata:
        # Get an image from https://picsum.photos
        response = urllib.request.urlopen("https://picsum.photos/id/237/300/300")
        profile_picture_path.write_bytes(response.read())

    return data.CurriculumVitae(
        name="John Doe",
        location="Istanbul, Turkey",
        email="john_doe@example.com",
        photo=profile_picture_path,  # type: ignore
        phone="+905419999999",  # type: ignore
        website="https://example.com",  # type: ignore
        social_networks=[
            data.SocialNetwork(network="LinkedIn", username="johndoe"),
            data.SocialNetwork(network="GitHub", username="johndoe"),
            data.SocialNetwork(network="Instagram", username="johndoe"),
            data.SocialNetwork(network="ORCID", username="0000-0000-0000-0000"),
            data.SocialNetwork(network="Google Scholar", username="F8IyYrQAAAAJ"),
            data.SocialNetwork(network="Mastodon", username="@johndoe@example.com"),
            data.SocialNetwork(network="StackOverflow", username="12323/johndoe"),
            data.SocialNetwork(network="GitLab", username="johndoe"),
            data.SocialNetwork(network="ResearchGate", username="johndoe"),
            data.SocialNetwork(network="YouTube", username="johndoe"),
            data.SocialNetwork(network="Telegram", username="johndoe"),
            data.SocialNetwork(network="X", username="johndoe"),
        ],
        sections={
            "Text Entries": [text_entry, text_entry, text_entry],
            "Bullet Entries": [bullet_entry, bullet_entry],
            "Publication Entries": create_combinations_of_a_model(
                data.PublicationEntry
            ),
            "Experience Entries": create_combinations_of_a_model(data.ExperienceEntry),
            "Education Entries": create_combinations_of_a_model(data.EducationEntry),
            "Normal Entries": create_combinations_of_a_model(data.NormalEntry),
            "One Line Entries": create_combinations_of_a_model(data.OneLineEntry),
            "Numbered Entries": create_combinations_of_a_model(data.NumberedEntry),
            "Reversed Numbered Entries": create_combinations_of_a_model(
                data.ReversedNumberedEntry
            ),
            "A Section & with % Special Characters": [
                data.NormalEntry(name="A Section & with % Special Characters")
            ],
        },
    )


@pytest.fixture
def jinja2_environment() -> jinja2.Environment:
    """Return a Jinja2 environment."""
    return templater.Jinja2Environment().environment


@pytest.fixture
def tests_directory_path() -> pathlib.Path:
    """Return the path to the tests directory."""
    return pathlib.Path(__file__).parent


@pytest.fixture
def root_directory_path(tests_directory_path) -> pathlib.Path:
    """Return the path to the repository's root directory."""
    return tests_directory_path.parent


@pytest.fixture
def testdata_directory_path(tests_directory_path) -> pathlib.Path:
    """Return the path to the testdata directory."""
    return tests_directory_path / "testdata"


@pytest.fixture
def specific_testdata_directory_path(testdata_directory_path, request) -> pathlib.Path:
    """Return the path to a specific testdata directory.

    For example, if the test function is named `test_rendercv`, this will return the
    path to the `testdata/test_rendercv` directory.
    """
    return testdata_directory_path / request.node.originalname


def are_these_two_directories_the_same(
    directory1: pathlib.Path, directory2: pathlib.Path
) -> bool:
    """Check if two directories are the same.

    Args:
        directory1: The first directory to compare.
        directory2: The second directory to compare.

    Raises:
        AssertionError: If the two directories are not the same.
    """
    for file1 in directory1.iterdir():
        if file1.name == "__pycache__":
            continue

        file2 = directory2 / file1.name
        if file1.is_dir():
            if not file2.is_dir():
                return False
            return are_these_two_directories_the_same(file1, file2)
        return are_these_two_files_the_same(file1, file2)

    return True


def are_these_two_files_the_same(file1: pathlib.Path, file2: pathlib.Path) -> bool:
    """Check if two files are the same.

    Args:
        file1: The first file to compare.
        file2: The second file to compare.

    Raises:
        AssertionError: If the two files are not the same.
    """
    extension1 = file1.suffix
    extension2 = file2.suffix

    if extension1 != extension2:
        return False

    if extension1 == ".pdf":
        pages1 = pypdf.PdfReader(file1).pages
        pages2 = pypdf.PdfReader(file2).pages
        result = len(pages1) == len(pages2)

        for i in range(len(pages1)):
            if pages1[i].extract_text() != pages2[i].extract_text():
                result = False
                break

        return result

    return filecmp.cmp(file1, file2)


@pytest.fixture
def run_a_function_and_check_if_output_is_the_same_as_reference(
    tmp_path: pathlib.Path,
    specific_testdata_directory_path: pathlib.Path,
) -> typing.Callable:
    """Run a function and check if the output is the same as the reference."""

    def function(
        function: typing.Callable,
        reference_file_or_directory_name: str,
        output_file_name: Optional[str] = None,
        generate_reference_files_function: Optional[typing.Callable] = None,
        **kwargs,
    ):
        output_is_a_single_file = output_file_name is not None
        if output_is_a_single_file:
            output_file_path = tmp_path / output_file_name

        reference_directory_path: pathlib.Path = specific_testdata_directory_path
        reference_file_or_directory_path = (
            reference_directory_path / reference_file_or_directory_name
        )

        # Update the testdata if update_testdata is True
        if update_testdata:
            # create the reference directory if it does not exist
            reference_directory_path.mkdir(parents=True, exist_ok=True)

            # remove the reference file or directory if it exists
            if reference_file_or_directory_path.is_dir():
                shutil.rmtree(reference_file_or_directory_path)
            elif reference_file_or_directory_path.exists():
                reference_file_or_directory_path.unlink()

            if generate_reference_files_function:
                generate_reference_files_function(
                    reference_file_or_directory_path, **kwargs
                )
            else:
                # copy the output file or directory to the reference directory
                function(tmp_path, reference_file_or_directory_path, **kwargs)
                if output_is_a_single_file:
                    shutil.move(output_file_path, reference_file_or_directory_path)  # type: ignore
                else:
                    shutil.move(tmp_path, reference_file_or_directory_path)
                    pathlib.Path.mkdir(tmp_path)

        function(tmp_path, reference_file_or_directory_path, **kwargs)

        if output_is_a_single_file:
            return are_these_two_files_the_same(
                output_file_path,  # type: ignore
                reference_file_or_directory_path,  # type: ignore
            )
        return are_these_two_directories_the_same(
            tmp_path, reference_file_or_directory_path
        )

    return function


@pytest.fixture
def input_file_path(tmp_path, testdata_directory_path) -> pathlib.Path:
    """Return the path to the input file."""
    # copy the input file to the temporary directory
    input_file_path = testdata_directory_path / "John_Doe_CV.yaml"
    # Update the auxiliary files if update_testdata is True
    if update_testdata:
        # create testdata directory if it doesn't exist
        if not input_file_path.parent.exists():
            input_file_path.parent.mkdir()

        input_dictionary = {
            "cv": {
                "name": "John Doe",
                "sections": {"test_section": ["this is a text entry."]},
            },
        }

        # dump the dictionary to a yaml file
        yaml_object = ruamel.yaml.YAML()
        yaml_object.dump(input_dictionary, input_file_path)

    shutil.copyfile(input_file_path, tmp_path / "John_Doe_CV.yaml")
    return tmp_path / "John_Doe_CV.yaml"


@pytest.fixture
def design_file_path(tmp_path, testdata_directory_path) -> pathlib.Path:
    """Return the path to the input file."""
    design_settings_file_path = testdata_directory_path / "John_Doe_CV_design.yaml"
    if update_testdata:
        design_settings_file_path.write_text("design:\n  theme: classic\n")

    shutil.copyfile(design_settings_file_path, tmp_path / "John_Doe_CV_design.yaml")
    return tmp_path / "John_Doe_CV_design.yaml"


@pytest.fixture
def locale_file_path(tmp_path, testdata_directory_path) -> pathlib.Path:
    """Return the path to the input file."""
    locale_file_path = testdata_directory_path / "John_Doe_CV_locale.yaml"
    if update_testdata:
        locale_file_path.write_text("locale:\n  years: yil\n")
    shutil.copyfile(locale_file_path, tmp_path / "John_Doe_CV_locale.yaml")
    return tmp_path / "John_Doe_CV_locale.yaml"


@pytest.fixture
def rendercv_settings_file_path(tmp_path, testdata_directory_path) -> pathlib.Path:
    """Return the path to the input file."""
    rendercv_settings_file_path = (
        testdata_directory_path / "John_Doe_CV_rendercv_settings.yaml"
    )
    if update_testdata:
        rendercv_settings_file_path.write_text(
            "rendercv_settings:\n  render_command:\n    dont_generate_html: true\n"
        )

    shutil.copyfile(
        rendercv_settings_file_path, tmp_path / "John_Doe_CV_rendercv_settings.yaml"
    )
    return tmp_path / "John_Doe_CV_rendercv_settings.yaml"
