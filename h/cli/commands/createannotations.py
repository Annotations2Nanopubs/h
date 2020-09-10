import datetime
import random

import click

from tests.common import factories


@click.command()
@click.pass_context
def createannotations(ctx):
    request = ctx.obj["bootstrap"]()
    db = request.db
    tm = request.tm

    for _ in range(100000):
        created = updated = datetime.datetime(
            year=2020,
            month=random.randint(1, 12),
            day=random.randint(1, 27),
            hour=random.randint(1, 12),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
        )
        db.add(factories.Annotation.build(created=created, updated=updated))

    tm.commit()
