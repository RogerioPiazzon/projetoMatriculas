@echo off & title %~nx0 & color 5F
SET mypath=%~dp0
echo %mypath:~0,-1%
echo %mypath:~0%

goto check_Permissions

:check_Permissions
    echo ATENCAO: Para o pleno funcionamento desse script e necessario permisoes de Administrador.
    echo Detectando permisoes...
    
    net session >nul 2>&1
    if %errorLevel% == 0 (
        goto :DOES_PYTHON_EXIST
    ) else (
        echo Falha: Permissao de Administrador necessaria.
        echo Por favor, reabra o script clicando com o botao direito,
        echo selecionando Executar como Administrador/Run as Administrator.
        PAUSE
        goto :EOF
    )
    
    pause >nul

    

goto :DOES_PYTHON_EXIST

:DOES_PYTHON_EXIST
echo Verificando instalacao do Python...
python -V | find /v "Python" >NUL 2>NUL && (goto :PYTHON_DOES_NOT_EXIST)
python -V | find "Python"    >NUL 2>NUL && (goto :PYTHON_DOES_EXIST)
goto :EOF

:PYTHON_DOES_NOT_EXIST
echo Python nao localizado!
echo Procurando arquivo de instalacao...
if not exist "%mypath:~0,-1%\resource\python-3.10.9-amd64.exe" (
    if not exist  "%userprofile%\Downloads\python-3.10.9-amd64.exe" ( 
        echo Arquivo de instalacao nao encontrado
        echo Iniciando download...
        start "" "https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe"
        echo Caso o download nao tiver sido iniciado por favor, acesse "https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe" e faca o download do python
        pause
        ) else (
            start /d "%userprofile%\Downloads\" python-3.10.9-amd64.exe  InstallAllUsers=1 PrependPath=1 Include_test=0
        )
) else (
    start /d "%mypath:~0,-1%\resource\" python-3.10.9-amd64.exe  InstallAllUsers=1 PrependPath=1 Include_test=0
)
goto :DOES_PYTHON_EXIST

:PYTHON_DOES_EXIST
for /f "delims=" %%V in ('python -V') do @set ver=%%V
echo Python instalado!
goto :VERIFYRESOURCES


:VERIFYRESOURCES
echo Criando ambiente virtual...
IF EXIST %mypath:~0,-1%\env RMDIR /S /Q %mypath:~0,-1%\env
python -m venv %mypath:~0,-1%\env
%mypath:~0,-1%\env\scripts\python.exe -m pip install --upgrade pip
call %mypath:~0,-1%\env\Scripts\activate.bat
echo Instalando pacotes necessarios...
pip install -r %mypath:~0,-1%\requirements.txt

if not exist "%mypath:~0,-1%\resultado" md "%mypath:~0,-1%\resultado"
goto:SELECTCREGISTRY


:SELECTCREGISTRY
set /p cartorio= "Qual o cartorio origem do documento? (default: GERAL) :"
echo Cartorio selecionado "%cartorio%"
goto :SELECTPATH


:SELECTPATH
echo Selecione uma pasta para analise
setlocal

set "psCommand="(new-object -COM 'Shell.Application')^
.BrowseForFolder(0,'Selecione a pasta com os arquivos para analise.',0,0).self.path""

for /f "usebackq delims=" %%I in (`powershell %psCommand%`) do set "folder=%%I"

setlocal enabledelayedexpansion
echo Analisando os arquivos da pasta !folder!

call %mypath:~0,-1%\env\Scripts\python.exe  %mypath:~0,-1%\src\information_extraction.py "%cartorio%" !folder!


endlocal

pause
