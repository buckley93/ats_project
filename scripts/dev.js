const path = require('path');
const { spawn } = require('child_process');

const root = path.resolve(__dirname, '..');
const isWindows = process.platform === 'win32';

const pythonPath = isWindows
  ? path.join(root, 'backend', 'ats_backend', 'Scripts', 'python.exe')
  : path.join(root, 'backend', 'ats_backend', 'bin', 'python');

const npmCommand = isWindows ? 'npm.cmd' : 'npm';

const backend = spawn(
  pythonPath,
  ['-m', 'uvicorn', 'app:app', '--reload', '--host', '0.0.0.0', '--port', '8000'],
  {
    cwd: path.join(root, 'backend'),
    stdio: 'inherit',
  }
);

const frontend = spawn(npmCommand, ['--prefix', path.join(root, 'frontend'), 'start'], {
  cwd: root,
  stdio: 'inherit',
  shell: isWindows,
});

let isShuttingDown = false;

function shutdown(exitCode) {
  if (isShuttingDown) {
    return;
  }
  isShuttingDown = true;

  if (!backend.killed) {
    backend.kill('SIGINT');
  }
  if (!frontend.killed) {
    frontend.kill('SIGINT');
  }

  process.exit(exitCode);
}

backend.on('exit', (code) => {
  shutdown(code || 0);
});

frontend.on('exit', (code) => {
  shutdown(code || 0);
});

process.on('SIGINT', () => shutdown(0));
process.on('SIGTERM', () => shutdown(0));
