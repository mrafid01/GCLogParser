@ECHO OFF
START "FlaskServer" cmd /c python ./BackEnd/LogParserAPI.py
START "WebUI" cmd /c python -m http.server 8080 -d ./Frontend