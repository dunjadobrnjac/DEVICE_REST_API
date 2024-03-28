export DATABASE_URL="sqlite:///data.db"
export JWT_KEY="15835791052248868013867479752485955126834265180411671240111600063995691199944"
flask db upgrade
waitress-serve --port=5000 wsgi:app
rm -f ./instance/data.db
