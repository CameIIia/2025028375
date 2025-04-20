from app import create_app
from flask import render_template
app = create_app()


if __name__ == '__main__':
    app.run(port=8282, debug=True)