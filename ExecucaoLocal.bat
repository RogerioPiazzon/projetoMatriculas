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
    if "%e%" NEQ "" (
        call :success_execution
    )
    exit /b

:status_execution
    call :header
    set execution_msgs[%e%].TASK=%nome_params%
    set execution_msgs[%e%].VALUE=%params%
    echo    %nome_params%:%params%
    exit /b

:success_execution
    echo  [EXECUCAO] 
    set /a "counter=%e%-1"
    for /l %%a in (0 , 1, %counter%) do (
        echo    !execution_msgs[%%a].TASK!:!execution_msgs[%%a].VALUE!
    )
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
    echo  [PREPARACAO] 
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
    echo     Python nao localizado!
    echo     Procurando arquivo de instalacao...
    if not exist "%mypath:~0,-1%\resource\python-3.10.9-amd64.exe" (
        if not exist  "%userprofile%\Downloads\python-3.10.9-amd64.exe" ( 
            echo     Arquivo de instalacao nao encontrado
            echo     Iniciando download...
            start "" "https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe"
            echo     Caso o download nao tiver sido iniciado por favor, acesse "https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe" e faca o download do python
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
    echo     Python instalado!
    goto :VERIFYRESOURCES


:VERIFYRESOURCES
    if not exist "%mypath:~0,-1%\resultado" md "%mypath:~0,-1%\resultado"
    set i=2
    set name_step=Baixando bibliotecas e criando ambiente virtual
    call :step_validation
    if exist "%mypath:~0,-1%\env\." ( 
            for /f "skip=5 tokens=1,2,4 delims= " %%a in ('dir /ad /tc "%mypath:~0,-1%\env\."') do IF "%%c"=="." (
                set "dt=%%a"
            )
    ) else ( 
        set "dt=19991020"
        )

    if %dt% == %date% (
        goto :CHECKTESSERACT
    )
    else (
        goto :DOWN_CREAT_ENV
    )

:DOWN_CREAT_ENV
    IF EXIST %mypath:~0,-1%\env RMDIR /S /Q %mypath:~0,-1%\env ELSE md %mypath:~0,-1%\env
    python -m venv %mypath:~0,-1%\env
    %mypath:~0,-1%\env\scripts\python.exe -m pip install --upgrade pip
    call %mypath:~0,-1%\env\Scripts\activate.bat
    echo     Instalando pacotes necessarios...
    pip install -r %mypath:~0,-1%\requirements.txt
    goto:CHECKTESSERACT


:CHECKTESSERACT
    set i=3
    set name_step=Instalando Tesseract...
    call :step_validation
    IF EXIST %ProgramFiles%\Tesseract-OCR IF exist %ProgramFiles%\Tesseract-OCR (
        goto:INSERTPATHENV
    )
    else (
        goto:INSTALL_TESSERACT
    )

:INSTALL_TESSERACT
    set i=3
    set name_step=Instalando Tesseract
    call :step_validation
    echo       Confirme as etapas na tela...      
    start %mypath:~0,-1%\resource\tesseract-ocr-w64-setup-5.3.1.20230401.exe
    goto:CHECKTESSERACT

:INSERTPATHENV
    set i=4
    set name_step=Ajustando variaveis de ambiente
    call :step_validation
    IF EXIST %ProgramFiles%\Tesseract-OCR (
        xcopy /Y "%mypath:~0,-1%\resource\por.traineddata" "%ProgramFiles%\Tesseract-OCR\tessdata\"
    ) ELSE (
        xcopy /Y "%mypath:~0,-1%\resource\por.traineddata" "%ProgramFiles(x86)%\Tesseract-OCR\tessdata\"
    )
    SET PATH="%PATH%;%mypath:~0,-1%\resource\poppler-23.08.0\Library\bin;%ProgramFiles%\Tesseract-OCR;%ProgramFiles(x86)%\Tesseract-OCR"
    pause
    set i=5
    goto:SELECTCREGISTRY

:SELECTCREGISTRY
    cls
    set e=0
    call :header
    set nome_params=CARTORIO
    set /p input= "    Qual o cartorio origem do documento? (default: GERAL) :"
    if "%input%"=="" (
        set params=GERAL
    ) else (
        set params=%input%
    )
    set cartorio=%params%
    call :status_execution
    goto :SELECTPATH


:SELECTPATH
    echo     Selecione uma pasta para analise
    setlocal
    set "psCommand="(new-object -COM 'Shell.Application').BrowseForFolder(0,'Selecione a pasta com os arquivos para analise.',0,0).self.path""
    for /f "usebackq delims=" %%I in (` start /B powershell %psCommand%`) do set "folder=%%I"
    setlocal enabledelayedexpansion
    echo Analisando os arquivos da pasta !folder!
    set e=1
    set nome_params=PASTA
    set params=!folder!
    call :status_execution
    goto :DOES_DOWNLOAD_PARAMS


:DOES_DOWNLOAD_PARAMS
    set e=2
    set nome_params=DOWNLOAD_PARAMETROS
    set /p input= "    Deseja fazer o download dos parametros carregados no google Drive? [Y/N]: (Default Y)"
    if "%input%"=="" (
        set params=Y
    ) else (
        set params=%input%
    )
    set down=%params%
    call :status_execution
    echo      Executando analise...      
    call %mypath:~0,-1%\env\Scripts\python.exe  %mypath:~0,-1%\src\information_extraction.py "%cartorio%" !folder! "%down%"


endlocal

pause
