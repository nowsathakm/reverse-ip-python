from flask import Flask, render_template, request
import psycopg2
import public_ip as ip
import os
import json

app = Flask(__name__)

# Fetch database connection details from environment variables
CONFIG_ENV = os.environ.get("CONFIG_ENV")
config_data = json.loads(CONFIG_ENV)

# Database connection details (replace with your own)
DB_NAME = config_data["DB_NAME"]
DB_USER = config_data["DB_USER"]
DB_PASSWORD = config_data["DB_PASSWORD"]
DB_HOST = config_data["DB_HOST"]
DB_PORT = config_data["DB_PORT"]

@app.route("/")
def reverse_ip():
  # Get client IP
  xff_header = request.headers.get('X-Forwarded-For')
  xri_header = request.headers.get('X-Real-IP')
  forwarded_header = request.headers.get('Forwarded')
  # Check if any of the headers are present
  if xff_header:
      client_ip = xff_header.split(',')[0].strip()
  elif xri_header:
      client_ip = xri_header
  elif forwarded_header:
      # Extracting client IP from Forwarded header, assuming the format is "for=<client_ip>"
      client_ip = forwarded_header.split('for=')[1].split(';')[0].strip('" ')
  else:
      # Fallback to remote address if none of the headers are present
      client_ip = request.remote_addr

  # Reverse the IP
  reversed_ip = ".".join(client_ip.split(".")[::-1])

  # Connect to database
  conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
  cur = conn.cursor()

  # Insert data into table (assuming a table named "ips" with columns "original_ip" and "reversed_ip")
  cur.execute("INSERT INTO reversed_ips (original_ip, reversed_ip) VALUES (%s, %s)", (client_ip, reversed_ip))
  conn.commit()

  # Retrieve recent reversed IPs (optional)
  cur.execute("SELECT * FROM reversed_ips ORDER BY id ASC")  # Order by ID
  reversed_ips = cur.fetchall()
  cur.close()
  conn.close()

  # Render the template with data
  return render_template("index.html", client_ip=client_ip, reversed_ip=reversed_ip, reversed_ips=reversed_ips)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
