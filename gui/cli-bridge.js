const http = require('http');
const { spawn } = require('child_process');
const path = require('path');

const PORT = Number(process.env.TILSAM_BRIDGE_PORT || 8787);
const repoRoot = path.resolve(__dirname, '..');
const srcPath = path.join(repoRoot, 'src');

function withPythonPath(env) {
  const current = env.PYTHONPATH || '';
  const sep = process.platform === 'win32' ? ';' : ':';
  const next = current ? `${srcPath}${sep}${current}` : srcPath;
  return { ...env, PYTHONPATH: next };
}

function runCommand(command, args) {
  return new Promise((resolve) => {
    const child = spawn(command, args, {
      cwd: repoRoot,
      env: withPythonPath(process.env),
      stdio: ['ignore', 'pipe', 'pipe'],
      shell: false,
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (chunk) => {
      stdout += chunk.toString('utf-8');
    });

    child.stderr.on('data', (chunk) => {
      stderr += chunk.toString('utf-8');
    });

    child.on('error', (error) => {
      resolve({ ok: false, code: null, stdout, stderr: `${stderr}${error.message}` });
    });

    child.on('close', (code) => {
      resolve({ ok: code === 0, code, stdout, stderr });
    });
  });
}

async function runTilsam(args) {
  const candidates = [
    { command: 'tilsam', args },
    { command: 'py', args: ['-m', 'tilsam.main', ...args] },
    { command: 'python', args: ['-m', 'tilsam.main', ...args] },
  ];

  let lastResult = null;

  for (const candidate of candidates) {
    const result = await runCommand(candidate.command, candidate.args);
    const missingCmd =
      result.code === null ||
      /not found|is not recognized|No such file or directory/i.test(result.stderr);

    if (result.ok) {
      return { ...result, command: candidate.command };
    }

    lastResult = { ...result, command: candidate.command };

    if (!missingCmd) {
      return lastResult;
    }
  }

  return lastResult || {
    ok: false,
    code: null,
    command: 'tilsam',
    stdout: '',
    stderr: 'Could not find a runnable Python/tilsam command.',
  };
}

function sendJson(res, statusCode, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
  });
  res.end(body);
}

function readJson(req) {
  return new Promise((resolve, reject) => {
    let raw = '';

    req.on('data', (chunk) => {
      raw += chunk.toString('utf-8');
      if (raw.length > 1_000_000) {
        reject(new Error('Request body too large'));
      }
    });

    req.on('end', () => {
      if (!raw) {
        resolve({});
        return;
      }

      try {
        resolve(JSON.parse(raw));
      } catch {
        reject(new Error('Invalid JSON body'));
      }
    });

    req.on('error', reject);
  });
}

const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.method !== 'POST' || req.url !== '/api/cli') {
    sendJson(res, 404, { error: 'Not found' });
    return;
  }

  try {
    const body = await readJson(req);
    const args = Array.isArray(body.args) ? body.args.map((v) => String(v)) : null;

    if (!args || args.length === 0) {
      sendJson(res, 400, { error: 'Body must include a non-empty args array.' });
      return;
    }

    const result = await runTilsam(args);

    if (!result.ok) {
      sendJson(res, 500, {
        ok: false,
        command: result.command,
        code: result.code,
        stdout: result.stdout,
        stderr: result.stderr,
      });
      return;
    }

    sendJson(res, 200, {
      ok: true,
      command: result.command,
      code: result.code,
      stdout: result.stdout,
      stderr: result.stderr,
    });
  } catch (error) {
    sendJson(res, 400, { error: error.message });
  }
});

server.listen(PORT, () => {
  console.log(`Tilsam CLI bridge listening on http://localhost:${PORT}`);
});
