const spawn = require('child_process').spawn;

// Main

const env = (process.env.TRAVIS) ? 'chrome,safari,edge' : 'chrome'
const server = spawn('make', ['app-e2e']);
const runner = spawn('./node_modules/.bin/nightwatch', ['-e', env], {stdio: 'inherit'});

runner.on('exit', function (code) {
  server.kill();
  process.exit(code);
});

runner.on('error', function (err) {
  server.kill();
  throw err;
});
