# Application build

Build produces two artefacts:

* Python wheel
* docker container
Application version is loaded from the [VERSION] file.

## Wheel

Wheel package is build with `hatch`.
All metadata is loaded from `kitchen_aid/__about__.py`
You can build it with

```bash
make build-py
```

## Docker image

Docker image is build in two steps - builder, which will generate the package dependencies and the actual resulting container.

## Dependencies

Repo contains two types of dependencies - application dependencies and dev environment dependencies.
Application dependencies are in [requirements.txt](../requirements.txt).
Dev environment dependencies are in [resources/dev-requirements.txt](../resources/dev-requirements.txt).
Make sure to place all packages, required for the test and build within the corresponding files.
