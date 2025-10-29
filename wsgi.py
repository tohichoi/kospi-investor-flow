from pathlib import Path
from data_analyzer import create_app, EXCEL_FILENAME

# Create Dash app using the local data file. Fly will run this WSGI app via gunicorn.
base = Path(__file__).parent
data_file = base / "data" / EXCEL_FILENAME
dash_app = create_app(data_file)

# Expose the Flask server object as `app` for WSGI servers (gunicorn)
app = dash_app.server
