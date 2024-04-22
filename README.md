# hl-cli

Hyperliquid CLI built in Python.

*not the final version of this code so expect it to be messy in some cases.*

*Only supports perps for now, spot support coming soon maybe

*I'll make this an executable one day, need to figure out how to manage credentials

## Initial setup instructions
- Install pyenv, follow instructions [here](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation)
- Install python 3.7.17 with pyenv (or pyenv-win for windows): `pyenv install 3.7.17`
- Install poetry, use the recommended instructions [here](https://python-poetry.org/docs/#installing-with-pipx) (at time of writing use pipx)
- Clone this repo into a directory of your choice, initiate your poetry environment with `poetry install && poetry shell` (recommended to run `poetry install` anytime you git pull updates to make sure your local environment is up to date)
- Start up your virtual environment with `poetry shell`
- Create a `.env` file in the root directory, this file will remain private to you as it is git ignored from being commited. Add `PRIVATE_KEY=<YOUR_PRIVATE_KEY>` into this file so that the cli tool can connect to your hyperliquid account.
- Run `hl-cli` to start up the Hyperliquid CLI interactive shell started

## Everyday instructions
- Run `poetry shell` to get your virtual environment started
- Run `hl-cli` to get the Hyperliquid CLI interactive shell started
- Run `help` if you need a list of available commands
- Run `<command> --help` for information on that particular command's argument options
- Note which arguments are optional, for example `long SOL --margin 500` will market buy SOL with $500 of margin at the maximum leverage by default. However, `long SOL --margin 500 --price 110` will limit buy SOL with $500 of margin with a limit price of $110.
