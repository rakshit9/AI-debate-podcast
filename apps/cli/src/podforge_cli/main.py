import typer

app = typer.Typer(name="podforge", help="PodForge CLI — AI podcast production platform")


@app.command()
def version() -> None:
    typer.echo("podforge-cli 0.1.0")


if __name__ == "__main__":
    app()
