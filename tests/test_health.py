import os


def test_project_structure():

    required = [
        "backend",
        "engines",
        "core",
        "docs",
        "scripts",
        "AI_CONTEXT.md",
        "STATUS.md",
        "TASK.md",
    ]


    missing = []


    for item in required:

        if not os.path.exists(item):
            missing.append(item)


    assert not missing, f"Missing project items: {missing}"



def test_environment():

    assert os.path.exists(
        "docker-compose.yml"
    )

