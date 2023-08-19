@echo off & title %~nx0 & color 5F
setlocal EnableDelayedExpansion
SET mypath=%~dp0
@REM echo %mypath:~0,-1%
@REM echo %mypath:~0%

goto check_Permissions


:header
    cls
    echo  ============================================================================
    echo                         Projeto Matriculas - Versao 0                       
    echo   ATENCAO: Para o pleno funcionamento e necessario executar esse script com 
    echo                        permissoes de Administrador.                         
    echo  ============================================================================
    call :success_validation
    exit /b

:status_execution
    call :header
    set execution_msgs[%i%]=%name_step%
    echo    PASSO %e% - %exec_step% - EM ANDAMENTO
    exit /b


:step_validation
    call :header
    set validation_msgs[%i%]=%name_step%
    set /a "ilocal=%i%+1"
    echo    PASSO %i% - %name_step% - EM ANDAMENTO
    exit /b

:error_validation
    echo     FALHA: %msg_error%
    exit /b

:success_validation
    echo  [VALIDACOES] 
    set /a "counter=%i%-1"
    for /l %%a in (0 , 1, %counter%) do (
        echo    PASSO %%a - !validation_msgs[%%a]! - OK !
    )
    exit /b

:check_Permissions
    set i=0
    set name_step=Validando acesso de Administrador
    call :step_validation 
    net session >nul 2>&1
    if %errorLevel% == 0 (
        goto :DOES_PYTHON_EXIST
    ) else (
        set msg_error=Permissao de Administrador necessaria.
        call :error_validation
        set msg_error=Por favor, reabra o script clicando com o botao direito,
        call :error_validation
        set msg_error=selecionando Executar como Administrador/Run as Administrator.
        call :error_validation
        PAUSE
        goto :EOF
    )
    
    pause >nul

    

@REM goto :DOES_PYTHON_EXIST

:DOES_PYTHON_EXIST
    set i=1
    set name_step=Verificando instalacao do Python
    call :step_validation 
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
set i=2
set name_step=Baixando bibliotecas e criando ambiente virtual
call :step_validation
IF EXIST %mypath:~0,-1%\env RMDIR /S /Q %mypath:~0,-1%\env
python -m venv %mypath:~0,-1%\env
%mypath:~0,-1%\env\scripts\python.exe -m pip install --upgrade pip
call %mypath:~0,-1%\env\Scripts\activate.bat
echo Instalando pacotes necessarios...
pip install -r %mypath:~0,-1%\requirements.txt

if not exist "%mypath:~0,-1%\resultado" md "%mypath:~0,-1%\resultado"
    set i=3
    goto:SELECTCREGISTRY

:SELECTCREGISTRY
set e=0
set nome_params=CARTORIO
set /p params= "    Qual o cartorio origem do documento? (default: GERAL) :"
call :status_execution
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
