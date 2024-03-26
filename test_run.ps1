del .\instance\data.db
$env:DATABASE_URL="sqlite:///data.db"
$env:JWT_KEY="15835791052248868013867479752485955126834265180411671240111600063995691199944"
flask db upgrade
flask run
del .\instance\data.db
