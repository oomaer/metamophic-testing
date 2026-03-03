const http = require('http');

const port = 3000;
const server = http.createServer((req, res) => {
  console.log(`[Port ${port}] ${req.method} ${req.url}`);
  console.log('Headers:', req.headers);

  if (req.url === '/' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      message: 'Success',
      status: 200
    }));
  } else if (req.url === '/data' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      data: 'test data',
      status: 200
    }));
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('404 Not Found');
  }
});

server.listen(port, () => {
  console.log(`Server A is listening on port ${port}`);
});
