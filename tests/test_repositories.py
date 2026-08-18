import os


def test_repository_layer_exists():

    assert os.path.exists(
        "core/repositories"
    )


def test_repository_files_exist():

    files = [

        "channel_repository.py",
        "content_repository.py",
        "workflow_repository.py"

    ]


    for file in files:

        path = os.path.join(
            "core/repositories",
            file
        )

        assert os.path.exists(path)

