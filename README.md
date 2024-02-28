# Kitchen aid

Kitchen aid is a robot that aims to assist me in my tasks at home.
It's second task is to be part of my journey in improving my Python skills.

## Concepts

Kitchen aid supports `commands` and `interact interfaces`.

### Commands

Commands are, well, commands.
They are executed and will provide a `Result`. `Results` carry the message as well as the errors and exit status.
Some commands may support undo/redo logic

### Interact Interfaces

Those are the mediums over which communication between kitchen aid and users are hapening.
Interact interfaces are able to receive commands with their arguments and would return the result to the user in async manner.

## Usage

To run some command with it's arguments:

```bash
python3 -m --command cmd -a arg1
```

This execution runs commands with little to no overhead (undo and retry logic is still applied when valid).

To start the application flow:

```bash
python3 -m --config config.yaml
```

## Development setup

Checkout the [Makefile](./Makefile). You will need `venv`

Start with running `make venv`.
This would build your virtual env. You will still need to activate it. Check the output of the command.

You can start kitchen aid with `make run`
Check the rest of the docs in [docs/](./docs/).
