# Build na AWS
 1. Atualizar o requirements.txt
    ```
    $ pip freeze > requirements.txt 
    ```
    No projeto django adicionar ['*'] na variavel ALLOWED_HOSTS

 2. Efetuar o commit de todo o projeto e subir para o repo remoto
 3. Criar uma instância do EC2 Linux-Ubuntu na AWS.
    3.1. Adicionar um ip stático para a instância do EC2
 4. Conectar via SSH à instância EC2.
 5. Atualizar o linux com o comando a seguir:
    ```
    $ sudo apt update 
    ```
 6. Efetuar o clone do projeto do github para o EC2
    ```
    $ git clone [endereco_repo_remoto] 
    ```
 7. Instalar o gerenciador de ambientes virtuais do python
    ```
    $ sudo apt install python3.10-venv
    ```
 8. Entrar no diretorio do projeto clonado do git
 9. Criar o ambiente virtual com o comando a seguir
    ```
    $ sudo python3 -m venv venv
    ```
 10. Ativar o ambiente virtual
        ```
        $ source venv/bin/activate
        ```
 11. Instalar as dependência usando o arquivo de requirements.txt
        ```
        (venv) $ pip install -r requirements.txt
        ```
 12. Criar o servico para aplicação
 13. Abilitar o serviço com o systemctl
 14. Adicionar proxy reverso para acesso externo a aplicação
 15. Configurar o AWS Route53 mapeando o domínio ao ip da aplicação 
 15. Adicionar certificado SSL certbot



