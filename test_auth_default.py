import google.auth
try:
    creds, project = google.auth.default()
    print("Default credentials found!")
    print("Project:", project)
    print("Creds type:", type(creds))
except Exception as e:
    print("Failed to get default credentials:", e)
