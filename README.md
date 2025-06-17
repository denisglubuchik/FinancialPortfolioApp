<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>

<h1>Financial Portfolio Management System</h1>

<p>A comprehensive microservices-based financial portfolio management platform that enables users to create, manage, and monitor their investment portfolios through a Telegram bot interface with real-time price alerts.</p>

<h2>🚀 Features</h2>
<ul>
    <li><strong>Telegram Bot Interface</strong>: Manage portfolios directly through Telegram</li>
    <li><strong>Real-time Price Monitoring</strong>: 15-minute price updates with instant alerts</li>
    <li><strong>Smart Notifications</strong>: 5% price change threshold with anti-spam protection</li>
    <li><strong>Microservices Architecture</strong>: Scalable, reliable, and maintainable system</li>
</ul>

<h2>🏗️ Architecture</h2>

<p>The system follows a microservices architecture with service isolation and async communication:</p>

<pre><code>Telegram Bot ↔ API Gateway ↔ [User, Portfolio, Notification, Market Data] Services
                    ↓
              RabbitMQ Message Broker
                    ↓
         [PostgreSQL DBs, Redis Cache]</code></pre>

<h3>Services</h3>
<ul>
    <li><strong>API Gateway</strong> (Port 7777): Request routing and service orchestration</li>
    <li><strong>User Service</strong> (Port 8001): User management and Telegram authentication</li>
    <li><strong>Portfolio Service</strong> (Port 8000): Portfolio CRUD operations and price monitoring</li>
    <li><strong>Notification Service</strong> (Port 8002): Alert processing and message delivery</li>
    <li><strong>Market Data Service</strong> (Port 8003): Price data fetching and caching</li>
    <li><strong>Telegram Bot</strong>: User interface and command processing</li>
</ul>

<h2>🛠️ Technology Stack</h2>

<h3>Backend</h3>
<ul>
    <li><strong>FastAPI</strong></li>
    <li><strong>FastStream</strong></li>
    <li><strong>SQLAlchemy + asyncpg</strong></li>
    <li><strong>Pydantic</strong></li>
    <li><strong>APScheduler</strong></li>
</ul>

<h3>Infrastructure</h3>
<ul>
    <li><strong>PostgreSQL</strong></li>
    <li><strong>Redis</strong></li>
    <li><strong>RabbitMQ</strong></li>
    <li><strong>Docker + Docker Compose</strong></li>
</ul>

<h3>Bot</h3>
<ul>
    <li><strong>aiogram</strong></li>
    <li><strong>aiogram-dialog</strong></li>
</ul>

<h2>🚀 Getting Started</h2>

<h3>Prerequisites</h3>
<ul>
    <li>Docker and Docker Compose</li>
    <li>Telegram Bot Token</li>
</ul>

<h3>Installation</h3>

<ol>
    <li><strong>Clone the repository:</strong></li>
    <pre><code>git clone https://github.com/denisglubuchik/FinancialPortfolioApp.git
cd FinancialPortfolioApp</code></pre>

<li><strong>Create environment configuration:</strong></li>
<pre><code>cp .env-docker-example .env-docker</code></pre>
<pre><code>cp .env-bot-example .env-bot</code></pre>
<p>Edit <code>.env-docker</code> and <code>.env-bot</code> with your configuration values</p>

<li><strong>Build and start services:</strong></li>
<pre><code>docker compose build
docker compose up</code></pre>

<li><strong>Verify services are running:</strong></li>
<pre><code># Check service health
docker compose ps</code></pre>
</ol>

<h3>Service Ports</h3>
<table>
    <tr>
        <th>Service</th>
        <th>Port</th>
        <th>Purpose</th>
    </tr>
    <tr>
        <td>API Gateway</td>
        <td>7777</td>
        <td>Main entry point</td>
    </tr>
    <tr>
        <td>Portfolio Service</td>
        <td>8000</td>
        <td>Portfolio management</td>
    </tr>
    <tr>
        <td>User Service</td>
        <td>8001</td>
        <td>User operations</td>
    </tr>
    <tr>
        <td>Notification Service</td>
        <td>8002</td>
        <td>Alert processing</td>
    </tr>
    <tr>
        <td>Market Data Service</td>
        <td>8003</td>
        <td>Price data</td>
    </tr>
    <tr>
        <td>Redis</td>
        <td>6380</td>
        <td>Cache/session store</td>
    </tr>
    <tr>
        <td>RabbitMQ</td>
        <td>5672</td>
        <td>Message broker</td>
    </tr>
</table>

<h2>📄 License</h2>
<p>This project is licensed under the MIT License. See the <code>LICENSE</code> file for more information.</p>

</body>
</html>

