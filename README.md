Documentação do Projeto - TDE da Disciplina de Arquitetura de Banco de Dados
1. Introdução
Este documento descreve a estrutura do banco de dados "catalogo_musical.db" e o programa em Python "ORMSQLAlchemyv4_final.py", desenvolvido como parte do Trabalho de Desenvolvimento Experimental (TDE) da disciplina de Arquitetura de Banco de Dados. O objetivo deste projeto é criar e popular um banco de dados para catalogar informações de músicas, álbuns e artistas, utilizando a biblioteca SQLAlchemy para ORM (Mapeamento Objeto-Relacional).
2. Estrutura do Banco de Dados
O banco de dados "catalogo_musical.db" contém três tabelas principais: artistas, albuns e uma tabela associativa artista_album. Abaixo estão descritas as tabelas e seus relacionamentos.
2.1. Tabela "artistas"
A tabela "artistas" armazena informações sobre os artistas e possui a seguinte estrutura:
- id: Chave primária do tipo inteiro.
- nome: Nome do artista, do tipo string.
2.2. Tabela "albuns"
A tabela "albuns" armazena informações sobre os álbuns e possui a seguinte estrutura:
- id: Chave primária do tipo inteiro.
- nome: Nome do álbum, do tipo string.
- ano_lancamento: Ano de lançamento do álbum, do tipo inteiro.
- coletanea: Booleano que indica se o álbum é uma coletânea.
2.3. Tabela "artista_album"
A tabela associativa "artista_album" relaciona artistas a álbuns, permitindo o relacionamento N:N. Sua estrutura é a seguinte:
- artista_id: Chave estrangeira referenciando a tabela "artistas".
- album_id: Chave estrangeira referenciando a tabela "albuns".
3. Descrição do Programa em Python
O programa "ORMSQLAlchemyv4_final.py" foi desenvolvido para realizar operações de inserção e manipulação de dados no banco de dados "catalogo_musical.db", utilizando a biblioteca SQLAlchemy para mapeamento objeto-relacional. Abaixo estão descritas as principais funções do programa.
3.1. População de Tabelas
O programa realiza a inserção de dados nas tabelas "artistas", "albuns" e "artista_album" a partir de arquivos externos. A função responsável pela inserção de dados lê os arquivos .csv e popula as tabelas utilizando SQLAlchemy.
3.2. Funções CRUD
O programa também implementa as funções de Create, Read, Update e Delete (CRUD) para manipulação dos dados nas tabelas. Essas operações permitem a inserção, leitura, atualização e exclusão de registros no banco de dados.
3.3. Uso do SQLAlchemy
SQLAlchemy é uma biblioteca Python usada para interagir com bancos de dados relacionais. O projeto utiliza o SQLAlchemy para realizar o mapeamento objeto-relacional (ORM), permitindo que o código Python interaja com o banco de dados de maneira mais intuitiva e orientada a objetos.
4. Conclusão
Este projeto demonstrou o uso de técnicas de mapeamento objeto-relacional para manipulação de dados em um banco de dados relacional. O uso do SQLAlchemy permitiu um código mais limpo e organizado, facilitando as operações de CRUD e a gestão do banco de dados musical. O banco de dados resultante armazena informações estruturadas sobre artistas, álbuns e suas respectivas associações.
