from flask import Flask
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)
print(f"Secret key: {app.secret_key}")