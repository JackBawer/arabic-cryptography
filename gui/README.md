# Tilsam React GUI

This folder contains the React frontend and a local Node bridge that executes the Python CLI.

## How It Works

- The React app calls `POST /api/cli`.
- `cli-bridge.js` receives the request and runs the `tilsam` CLI command.
- The bridge tries these commands in order:
	- `tilsam ...`
	- `py -m tilsam.main ...`
	- `python -m tilsam.main ...`

## Run In Development

From this `gui` folder, open two terminals.

Terminal 1 (bridge):

```sh
npm run bridge
```

Terminal 2 (React):

```sh
npm start
```

Then open <http://localhost:3000>.

## Requirements

- Python 3.10+
- Node.js and npm
- `tilsam` Python package available in your environment (`pip install -e ..` from repo root recommended)

## Available Scripts

- `npm run bridge`: starts the CLI bridge on port `8787`
- `npm start`: starts the React dev server on port `3000`
- `npm run build`: production build
- `npm test`: test runner
