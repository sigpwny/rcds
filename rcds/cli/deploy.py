from sys import exit

import click

import rcds
import rcds.challenge.docker
from rcds.util import SUPPORTED_EXTENSIONS, find_files


@click.command()
@click.option('--delete/--no-delete', default=False)
def deploy(delete: bool) -> None:
    try:
        project_config = find_files(["rcds"], SUPPORTED_EXTENSIONS, recurse=True)[
            "rcds"
        ].parent
    except KeyError:
        click.echo("Could not find project root!")
        exit(1)
    click.echo(f"Loading project at {project_config}")
    project = rcds.Project(project_config)
    click.echo("Initializing backends")
    project.load_backends()
    click.echo("Loading challenges")
    project.load_all_challenges()
    for challenge in project.challenges.values():
        cm = rcds.challenge.docker.ContainerManager(challenge)
        for subcontainer_name, subcontainer in cm.subcontainers.items():
            click.echo(f"{challenge.config['id']}: checking container {subcontainer_name}")
            if not subcontainer.is_built():
                click.echo(
                    f"{challenge.config['id']}: building container {subcontainer_name}"
                    f" ({subcontainer.get_full_tag()})"
                )
                subcontainer.build()
        challenge.create_transaction().commit()
    if project.container_backend is not None:
        click.echo("Commiting container backend")
        project.container_backend.commit(delete)
    else:
        click.echo("WARN: no container backend, skipping...")
    if project.scoreboard_backend is not None:
        click.echo("Commiting scoreboard backend")
        project.scoreboard_backend.commit(delete)
    else:
        click.echo("WARN: no scoreboard backend, skipping...")
