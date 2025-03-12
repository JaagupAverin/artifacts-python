from pathlib import Path
from typing import Protocol, override

import httpx
import trio

JURA = "Jura"


def read_token() -> str:
    return Path("token.txt").read_text()


def get_character_url(character: str, action: str | None) -> str:
    if action:
        return f"https://api.artifactsmmo.com/my/{character}/action/{action}"
    return f"https://api.artifactsmmo.com/my/{character}"


class Action(Protocol):
    async def execute(self, client: httpx.AsyncClient, args: dict[str, str]) -> dict[str, str]: ...
    async def post_process(self, response: httpx.Response) -> dict[str, str]: ...


class SimpleAction(Action):
    def __init__(
        self,
        method: str,
        character: str,
        action: str | None,
        args: dict[str, str] | None = None,
    ) -> None:
        self.method: str = method
        self.character: str = character
        self.action: str | None = action
        self.args: dict[str, str] = args if args else {}

    @override
    async def execute(
        self,
        client: httpx.AsyncClient,
        args: dict[str, str] | None = None,
    ) -> dict[str, str]:
        if self.args and args:
            self.args.update(args)

        return await self.post_process(
            response=await client.request(
                method=self.method,
                url=get_character_url(character=self.character, action=self.action),
                json=self.args,
            )
        )

    @override
    async def post_process(self, response: httpx.Response) -> dict[str, str]:
        return response.json()


class ComplexAction:
    def __init__(self, actions: list[Action]) -> None:
        self.actions: list[Action] = actions

    async def execute(self, client: httpx.AsyncClient) -> None:
        args: dict[str, str] = {}
        for action in self.actions:
            args = await action.execute(client, args)
            print(args)


class GetPositionAction(SimpleAction):
    def __init__(self, character: str) -> None:
        super().__init__(
            method="GET",
            character=character,
            action=None,
        )

    @override
    async def post_process(self, response: httpx.Response) -> dict[str, str]:
        json: dict[str, str] = await super().post_process(response)
        return {
            "x": json["x"],
            "y": json["y"],
        }


class MoveAction(SimpleAction):
    def __init__(self, character: str, x: int, y: int) -> None:
        super().__init__(
            method="POST",
            character=character,
            action="move",
            args={
                "x": str(x),
                "y": str(y),
            },
        )


async def main() -> None:
    async with httpx.AsyncClient(
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {read_token()}",
        }
    ) as client:
        await move(client, JURA, 0, 1)


if __name__ == "__main__":
    trio.run(async_fn=main)

# TODO1: Fixup this stuff and get it running.
# https://docs.artifactsmmo.com/quickstart/first_fight
# https://api.artifactsmmo.com/openapi.json

