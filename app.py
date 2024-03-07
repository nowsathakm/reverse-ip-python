from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

# Database connection details (replace with your own)
DB_NAME = "reverseipdb"
DB_USER = "devdb_user"
DB_PASSWORD = "NowsTest890"
DB_HOST = "reverseipdb.czuiuosca5yf.eu-north-1.rds.amazonaws.com"
DB_PORT = "5432"

@app.route("/")
def reverse_ip():
  # Get client IP
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