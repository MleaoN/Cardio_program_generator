import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(__file__))

from cardio_app.webapp import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
