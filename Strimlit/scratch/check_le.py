with open("app.py", "rb") as f:
    sample = f.read(5000)
    print("CRLF in app.py:", b"\r\n" in sample)
