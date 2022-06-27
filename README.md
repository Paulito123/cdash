# cdash
A dashboard reflecting a status of a set of miners, validators or nodes. 

Inspired by:
  - https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login#step-2-creating-the-main-app-file
  - https://pypi.org/project/Flask-Login/
  - https://pythonbasics.org/flask-login/
  - https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/
  - https://hackersandslackers.com/series/build-flask-apps/
  - https://chartio.com/resources/tutorials/how-to-execute-raw-sql-in-sqlalchemy/


# I <know how to do it!
#
# 1. Make the channel public, set up a username for it.
# 2. Add any bot to the channel.
# 3. Go to the link
# https://api.telegram.org/bot[ТОКЕН_БОТА]/sendMessage?chat_id=@[USERNAME_КАНАЛА]&text=тест
# . After clicking the link the channel id will be displayed, save it.
# 4. Make the channel private.
# 5. Send messages like this:
# https://api.telegram.org>/bot[ТОКЕН_БОТА]/sendMessage?chat_id=@[ID_КАНАЛА]&text=тест.