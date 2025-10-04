Smart Queue Project

A web-based queue management system built using Flask, SQLite, and Socket.IO that allows users to take tokens, track their queue status in real-time, and lets staff manage token calls efficiently. Includes a QR code feature to quickly navigate users to the home page.

Features

Get Token: Users can generate a token number for the queue.

Real-time Updates: Users see the status of their token (waiting, called, served) updated instantly using WebSockets.

Staff Dashboard: Staff can call the next token and monitor currently serving tokens and waiting tokens.

Estimated Wait Time: Users can see the estimated waiting time based on tokens ahead.

QR Code Navigation: Users can scan a QR code to navigate to the home page from anywhere.

Lightweight Database: Uses SQLite for storing tokens.


Tech Stack

Backend: Flask, Flask-SocketIO

Database: SQLite

Frontend: HTML, CSS, JavaScript (Socket.IO)

QR Codes: qrcode Python library

Deployment/Test: ngrok (for real-device testing)
