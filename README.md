Financial Portfolio Managment App
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>README</title>
</head>
<body>

<h1>Microservices Architecture Project with FastAPI, FastStream, and RabbitMQ</h1>

<p>This project implements a microservices architecture using FastAPI, FastStream, and RabbitMQ for asynchronous messaging. The system allows for user creation financial portfolio and management its assets.</p>



<h2>Architecture</h2>
<p>The project consists of multiple microservices:</p>
<ul>
<h3>Backend:</h3>
<li><strong>API gateway</strong>: Redirects requests to the required service - <strong>IN PROGRESS</strong></li>
    <li><strong>User Service</strong>: Manages work with users.</li>
    <li><strong>Portfolio Service</strong>: Provides portfolio management features.</li>
    <li><strong>Analytics Service</strong>: Collects and analyzes user and portfolio data - <strong>IN PROGRESS</strong></li>
    <li><strong>Notification Service</strong>: Sends notifications - <strong>IN PROGRESS</strong></li>
<h3>Frontend:</h3>
<li><strong>Frontend Service - IN PROGRESS</strong></li>
</ul>

<h2>Getting Started</h2>

<h3>Installation</h3>

<ol>
    <li>Clone the repository:</li>
    <pre><code>git clone https://github.com/your-username/your-repo.git</code></pre>

    <li>Navigate to the project directory:</li>
    <pre><code>cd your-repo</code></pre>

    <li>Create .env-docker file using .env-docker-example</li>

    <li>Run docker compose</li>
    <pre><code>docker compose build && docker compose up</code></pre>
</ol>



<h2>License</h2>
<p>This project is licensed under the MIT License. See the <code>LICENSE</code> file for more information.</p>

</body>
</html>

