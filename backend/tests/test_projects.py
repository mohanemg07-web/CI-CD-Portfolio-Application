REQUIRED_FIELDS = {
    "id",
    "title",
    "description",
    "tech_stack",
    "github_url",
    "live_url",
    "year",
}


def test_projects_returns_list(client):
    response = client.get("/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_projects_each_has_required_fields(client):
    projects = client.get("/projects").json()
    for project in projects:
        missing = REQUIRED_FIELDS - set(project.keys())
        assert not missing, f"Project {project.get('id')} missing fields: {missing}"
        assert isinstance(project["tech_stack"], list)
        assert len(project["tech_stack"]) >= 1


def test_projects_returns_four(client):
    projects = client.get("/projects").json()
    assert len(projects) == 4
