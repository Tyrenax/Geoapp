@echo off
rem Geo Atlas : sert le jeu (web\dist) sur http://127.0.0.1:8405 et ouvre le navigateur.
rem Garder toujours la meme adresse : la progression est enregistree par le navigateur pour cette adresse.
rem GEOATLAS_NO_BROWSER=1 : ne pas ouvrir le navigateur ; GEOATLAS_PORT : autre port (tests).
setlocal
if not defined GEOATLAS_PORT set "GEOATLAS_PORT=8405"
set "DIST=%~dp0web\dist"
set "URL=http://127.0.0.1:%GEOATLAS_PORT%/"
if not exist "%DIST%\index.html" (
  rem Premier lancement apres un clone : installer et compiler, il faut Node.js.
  where npm >nul 2>nul || (
    echo Il faut Node.js pour compiler le jeu au premier lancement : https://nodejs.org
    pause
    exit /b 1
  )
  echo Premier lancement : installation et compilation du jeu, une minute...
  pushd "%~dp0web"
  if not exist node_modules call npm ci --no-audit --no-fund
  call npm run build
  popd
)
if not exist "%DIST%\index.html" (
  echo La compilation a echoue : voir les messages ci-dessus.
  pause
  exit /b 1
)
set "PY=py -3"
where py >nul 2>nul || set "PY=python"
powershell -NoProfile -Command "try { $c = New-Object Net.Sockets.TcpClient('127.0.0.1', %GEOATLAS_PORT%); $c.Close(); exit 0 } catch { exit 1 }"
if %errorlevel%==0 (
  echo Geo Atlas tourne deja sur %URL%
  if not "%GEOATLAS_NO_BROWSER%"=="1" start "" "%URL%"
  exit /b 0
)
if not "%GEOATLAS_NO_BROWSER%"=="1" start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 1; Start-Process '%URL%'"
echo Geo Atlas : %URL%   (fermer cette fenetre pour arreter le jeu)
%PY% -m http.server %GEOATLAS_PORT% --bind 127.0.0.1 --directory "%DIST%"
