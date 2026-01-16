const http = require('http');

port = 3001

const server = http.createServer((req, res) => {
  // Check if the request is a GET method and the path is '/'
  if (req.url === '/' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      message: `Success from 3000`,
      status: 200
    }));
  } else {
    // Handle other routes or methods with a 404
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('404 Not Found');
  }
});

server.listen(port, () => {
  console.log(`Server is listening on port ${port}`);
});