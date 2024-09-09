from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from tabulate import tabulate

Base = declarative_base()

# Tabela associativa entre Artista e Álbum (Relacionamento N:N)
artista_album = Table('artista_album', Base.metadata,
                      Column('artista_id', Integer, ForeignKey('artistas.id'), primary_key=True),
                      Column('album_id', Integer, ForeignKey('albuns.id'), primary_key=True)
                      )

# Tabela associativa entre Artista e Música (Relacionamento N:N para coletâneas)
artista_musica = Table('artista_musica', Base.metadata,
                       Column('artista_id', Integer, ForeignKey('artistas.id'), primary_key=True),
                       Column('musica_id', Integer, ForeignKey('musicas.id'), primary_key=True)
                       )

# Classes do modelo de dados
class Artista(Base):
    __tablename__ = 'artistas'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    albuns = relationship('Album', secondary=artista_album, back_populates='artistas')
    musicas = relationship('Musica', secondary=artista_musica, back_populates='artistas')

class Album(Base):
    __tablename__ = 'albuns'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    ano_lancamento = Column(Integer)
    coletanea = Column(Boolean, default=False)
    musicas = relationship('Musica', back_populates='album', cascade="all, delete-orphan")
    artistas = relationship('Artista', secondary=artista_album, back_populates='albuns')

class Musica(Base):
    __tablename__ = 'musicas'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    duracao = Column(Integer)  # Duração da música em segundos
    faixa = Column(Integer)  # Número da faixa no álbum
    album_id = Column(Integer, ForeignKey('albuns.id'))
    genero_id = Column(Integer, ForeignKey('generos.id'))
    album = relationship('Album', back_populates='musicas')
    genero = relationship('Genero', back_populates='musicas')
    artistas = relationship('Artista', secondary=artista_musica, back_populates='musicas')

class Genero(Base):
    __tablename__ = 'generos'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    musicas = relationship('Musica', back_populates='genero')

# Função para criar o banco de dados
def setup_database():
    engine = create_engine('sqlite:///musica_catalogo.db')
    Base.metadata.create_all(engine)
    return engine

# Função para iniciar sessão do banco de dados
def start_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

# Função para mostrar tabela usando Tabulate
def show_table(data, headers):
    print(tabulate(data, headers, tablefmt="pretty"))

# Função genérica para buscar registros
def fetch_records(session, entity_class):
    return session.query(entity_class).all()

# Função para verificar se o banco de dados está vazio
def is_database_empty(session):
    return not any([session.query(Artista).count(), session.query(Album).count(),
                    session.query(Musica).count(), session.query(Genero).count()])

# Função para mostrar o acervo completo, incluindo coletâneas
def show_acervo(session):
    if is_database_empty(session):
        print("Nenhuma informação disponível.")
    else:
        # Buscar todos os artistas
        artistas = fetch_records(session, Artista)
        if not artistas:
            print("Nenhum artista disponível.")
            return

        # Iterar sobre os artistas e exibir os álbuns associados a cada um
        for artista in artistas:
            print(f"Artista: {artista.nome}")

            if not artista.albuns:
                print("  Nenhum álbum associado a este artista.")
                continue

            for album in artista.albuns:
                print(f"  Álbum: {album.nome} ({album.ano_lancamento}) - {'Coletânea' if album.coletanea else 'Solo'}")

                if not album.musicas:
                    print("    Nenhuma música associada a este álbum.")
                    continue

                # Mostrar todas as músicas associadas ao álbum
                for musica in album.musicas:
                    genero_nome = musica.genero.nome if musica.genero else "Sem Gênero"
                    print(f"    Faixa {musica.faixa}: {musica.nome} - {musica.duracao} segundos (Gênero: {genero_nome})")

        # Exibir as coletâneas (álbuns que são marcados como coletâneas)
        coletaneas = session.query(Album).filter_by(coletanea=True).all()
        if coletaneas:
            print("\nColetâneas:")
            for album in coletaneas:
                print(f"  Álbum: {album.nome} ({album.ano_lancamento}) - Coletânea")
                if not album.musicas:
                    print("    Nenhuma música associada a esta coletânea.")
                    continue
                for musica in album.musicas:
                    genero_nome = musica.genero.nome if musica.genero else "Sem Gênero"
                    artistas = ", ".join([artista.nome for artista in musica.artistas])
                    # Converter a duração para minutos e segundos
                    minutos = musica.duracao // 60  # Divisão inteira
                    segundos = musica.duracao % 60  # Resto da divisão

                    # Formatar o tempo em MM:SS
                    duracao_formatada = f"{minutos:02}:{segundos:02}"
                    print(f"    Faixa {musica.faixa}: {musica.nome} - {artistas} (Duração: {duracao_formatada}, Gênero: {genero_nome})")

# Funções para mostrar apenas os gêneros, artistas, álbuns e músicas
def show_genero(session):
    generos = fetch_records(session, Genero)
    if not generos:
        print("Nenhuma informação disponível.")
    else:
        show_table([[genero.id, genero.nome] for genero in generos], ["ID", "Nome"])

def show_artista(session):
    artistas = fetch_records(session, Artista)
    if not artistas:
        print("Nenhuma informação disponível.")
    else:
        show_table([[artista.id, artista.nome] for artista in artistas], ["ID", "Nome"])

def show_album(session):
    albuns = fetch_records(session, Album)
    if not albuns:
        print("Nenhuma informação disponível.")
    else:
        show_table([[album.id, album.nome, album.ano_lancamento] for album in albuns], ["ID", "Nome", "Ano"])

def show_musica(session):
    musicas = session.query(Musica).all()

    if not musicas:
        print("Nenhuma informação disponível.")
    else:
        data = []
        for musica in musicas:
            album = session.get(Album, musica.album_id)
            if album:  # Verificar se o álbum ainda existe
                artistas = ", ".join([artista.nome for artista in musica.artistas])
                genero = session.get(Genero, musica.genero_id).nome if musica.genero else "Sem Gênero"

                # Converter a duração para minutos e segundos
                minutos = musica.duracao // 60  # Divisão inteira
                segundos = musica.duracao % 60  # Resto da divisão

                # Formatar o tempo em MM:SS
                duracao_formatada = f"{minutos:02}:{segundos:02}"

                # Adicionar os dados na lista, incluindo o ID da música
                data.append([musica.id, musica.nome, artistas, album.nome, album.ano_lancamento, duracao_formatada, genero])
            else:
                # Tratar o caso em que o álbum foi excluído
                data.append([musica.id, musica.nome, "Álbum excluído", "Álbum excluído", "N/A", musica.duracao, "N/A"])

        # Mostrar a tabela com as informações
        headers = ["ID", "Música", "Artista", "Álbum", "Ano", "Duração", "Gênero"]
        print(tabulate(data, headers=headers, tablefmt="pretty"))

# Funções CRUD para Gênero, Artista, Álbum e Música
def create_genero(session):
    while True:
        nome = input("Nome do Gênero: ")
        genero = Genero(nome=nome)
        session.add(genero)
        session.commit()
        print(f"Gênero '{nome}' cadastrado com sucesso!")
        if input("Cadastrar outro gênero? (s/n): ").lower() != 's':
            break

def create_artista(session):
    while True:
        nome = input("Nome do Artista: ")
        artista = Artista(nome=nome)
        session.add(artista)
        session.commit()
        print(f"Artista '{nome}' cadastrado com sucesso!")
        if input("Cadastrar outro artista? (s/n): ").lower() != 's':
            break

# Função para cadastrar álbum e associar músicas a artistas
def create_album(session):
    # Solicitar informações do álbum
    nome_album = input("Nome do Álbum: ")
    ano_album = input("Ano do Álbum: ")
    coletanea = input("O álbum é uma coletânea? (s/n): ").lower() == 's'

    # Criação do álbum no banco de dados
    album = Album(nome=nome_album, ano_lancamento=ano_album, coletanea=coletanea)
    session.add(album)
    session.commit()

    if not coletanea:
        # Caso o álbum seja de um único artista, associar o artista uma única vez
        show_artista(session)  # Mostrar lista de artistas existentes
        artista_id = input("Digite o ID do artista para associar ao álbum ou pressione Enter para cadastrar novo: ")

        if not artista_id:
            # Se o artista não existe, criar um novo
            create_artista(session)
            show_artista(session)  # Mostrar lista atualizada de artistas
            artista_id = input("Digite o ID do artista: ")

        # Associar o artista ao álbum
        artista = session.get(Artista, artista_id)
        if artista:
            album.artistas.append(artista)
            session.commit()  # Salvar a associação entre o artista e o álbum no banco de dados
            print(f"Álbum '{nome_album}' associado ao artista '{artista.nome}' com sucesso!")

    # Cadastro das músicas para o álbum
    while True:
        nome_musica = input("Nome da música: ")
        faixa = int(input("Número da faixa: "))
        duracao = int(input("Duração da música (em segundos): "))

        # Mostrar gêneros existentes
        show_genero(session)
        genero_id = input("Digite o ID do gênero ou pressione Enter para cadastrar novo: ")
        if not genero_id:
            create_genero(session)
            show_genero(session)
            genero_id = input("Digite o ID do gênero: ")

        # Para coletâneas, o artista deve ser solicitado a cada nova música
        if coletanea:
            show_artista(session)  # Mostrar lista de artistas existentes
            artista_id = input("Digite o ID do artista para associar à música ou pressione Enter para cadastrar novo: ")

            if not artista_id:
                create_artista(session)
                show_artista(session)  # Mostrar lista atualizada de artistas
                artista_id = input("Digite o ID do artista: ")

            artista = session.get(Artista, artista_id)
        else:
            # Se não for coletânea, usa o mesmo artista já associado ao álbum
            artista = album.artistas[0]  # O único artista do álbum

        # Criar a música e associar ao álbum e ao artista
        musica = Musica(nome=nome_musica, faixa=faixa, duracao=duracao, album_id=album.id, genero_id=genero_id)
        session.add(musica)
        session.commit()

        # Verificar se o artista já está associado à música, associando se necessário
        if artista not in musica.artistas:
            musica.artistas.append(artista)
            session.commit()

        print(f"Música '{nome_musica}' cadastrada no álbum '{album.nome}' e associada ao artista '{artista.nome}'.")

        # Verificar se deseja adicionar mais músicas
        if input("Cadastrar outra música? (s/n): ").lower() != 's':
            break

def create_musica(session):
    albuns = session.query(Album).all()

    if albuns:
        # Mostrar álbuns existentes
        print("Álbuns existentes:")
        show_table([[album.id, album.nome] for album in albuns], ["ID", "Nome"])

        # Pedir o ID do álbum
        album_id = input("Digite o ID do álbum para cadastrar a música: ")
        album = session.get(Album, album_id)

        if album:
            # Continuar com o cadastro da música
            nome_musica = input("Nome da música: ")
            duracao = int(input("Duração da música (em segundos): "))
            faixa = int(input("Número da faixa: "))
            ano_lancamento = int(input("Ano de lançamento da música: "))

            # Mostrar gêneros existentes
            show_genero(session)
            genero_id = input("Digite o ID do gênero ou pressione Enter para cadastrar novo: ")
            if not genero_id:
                create_genero(session)
                show_genero(session)
                genero_id = input("Digite o ID do gênero: ")

            # Criar a música e associar ao álbum
            musica = Musica(nome=nome_musica, faixa=faixa, duracao=duracao, album_id=album.id, genero_id=genero_id)
            session.add(musica)
            session.commit()

            # Verificar se o álbum é uma coletânea (múltiplos artistas)
            if album.coletanea:
                # Perguntar o artista para cada música em coletâneas
                show_artista(session)  # Mostrar lista de artistas existentes
                artista_id = input("Digite o ID do artista para associar à música ou pressione Enter para cadastrar novo: ")

                if not artista_id:
                    create_artista(session)
                    show_artista(session)
                    artista_id = input("Digite o ID do artista: ")

                artista = session.get(Artista, artista_id)
                if artista:
                    # Associar o artista à música
                    musica.artistas.append(artista)
                    session.commit()
                    print(f"Música '{nome_musica}' associada ao artista '{artista.nome}' na coletânea '{album.nome}'!")
                else:
                    print("Artista não encontrado.")
            else:
                # Para álbuns de um único artista, associar o artista ao álbum
                if len(album.artistas) > 0:
                    artista = album.artistas[0]  # Pegando o único artista do álbum
                    musica.artistas.append(artista)
                    session.commit()
                    print(f"Música '{nome_musica}' associada ao artista '{artista.nome}' no álbum '{album.nome}'!")
                else:
                    print("Nenhum artista associado ao álbum. Atualize o álbum com um artista.")

        else:
            print("Álbum não encontrado.")
    else:
        print("Nenhum álbum disponível. É necessário cadastrar um álbum primeiro.")


# Funções para atualizar informações no banco de dados
def update_info(session):
    if is_database_empty(session):
        print("Nenhuma informação disponível.")
    else:
        print("Escolha a opção de atualização:")
        print("1. Atualizar Artista")
        print("2. Atualizar Álbum")
        print("3. Atualizar Gênero")
        print("4. Atualizar Música")

        choice = input("Digite sua escolha: ")

        if choice == '1':
            # Atualizar Artista
            show_artista(session)
            artista_id = input("Digite o ID do artista que deseja atualizar: ")
            artista = session.get(Artista, artista_id)
            if artista:
                novo_nome = input(f"Nome atual: {artista.nome}. Digite o novo nome (ou Enter para manter o atual): ")
                if novo_nome:
                    artista.nome = novo_nome
                session.commit()
                print("Artista atualizado com sucesso!")
            else:
                print("Artista não encontrado.")

        elif choice == '2':
            # Atualizar Álbum e associar Artista
            show_album(session)
            album_id = input("Digite o ID do álbum que deseja atualizar: ")
            album = session.get(Album, album_id)
            if album:
                novo_nome = input(f"Nome atual: {album.nome}. Digite o novo nome (ou Enter para manter o atual): ")
                novo_ano = input(f"Ano atual: {album.ano_lancamento}. Digite o novo ano (ou Enter para manter o atual): ")
                if novo_nome:
                    album.nome = novo_nome
                if novo_ano:
                    album.ano_lancamento = novo_ano

                # Associar artista ao álbum
                show_artista(session)
                artista_id = input("Digite o ID do artista para associar ao álbum ou pressione Enter para manter o atual: ")
                if artista_id:
                    artista = session.get(Artista, artista_id)
                    if artista:
                        # Verificar se o artista já está associado ao álbum
                        if artista not in album.artistas:
                            album.artistas.append(artista)
                            session.commit()
                            print(f"Álbum '{album.nome}' associado ao artista '{artista.nome}' com sucesso!")
                    else:
                        print("Artista não encontrado.")

                session.commit()
                print("Álbum atualizado com sucesso!")
            else:
                print("Álbum não encontrado.")

        elif choice == '3':
            # Atualizar Gênero
            show_genero(session)
            genero_id = input("Digite o ID do gênero que deseja atualizar: ")
            genero = session.get(Genero, genero_id)
            if genero:
                novo_nome = input(f"Nome atual: {genero.nome}. Digite o novo nome (ou Enter para manter o atual): ")
                if novo_nome:
                    genero.nome = novo_nome
                session.commit()
                print("Gênero atualizado com sucesso!")
            else:
                print("Gênero não encontrado.")

        elif choice == '4':
            # Atualizar Música e Associar Artista
            show_musica(session)
            musica_id = input("Digite o ID da música que deseja atualizar: ")
            musica = session.get(Musica, musica_id)
            if musica:
                # Atualizar os atributos da música
                novo_nome = input(f"Nome atual: {musica.nome}. Digite o novo nome (ou Enter para manter o atual): ")
                nova_duracao = input(f"Duração atual: {musica.duracao}. Digite a nova duração (ou Enter para manter o atual): ")
                nova_faixa = input(f"Faixa atual: {musica.faixa}. Digite a nova faixa (ou Enter para manter a atual): ")
                if novo_nome:
                    musica.nome = novo_nome
                if nova_duracao:
                    musica.duracao = int(nova_duracao)
                if nova_faixa:
                    musica.faixa = int(nova_faixa)

                # Mostrar artistas existentes e associar à música
                show_artista(session)
                artista_id = input("Digite o ID do artista para associar à música ou pressione Enter para manter o atual: ")
                if artista_id:
                    artista = session.get(Artista, artista_id)
                    if artista:
                        # Verificar se o artista já está associado à música
                        if artista not in musica.artistas:
                            musica.artistas.append(artista)
                            session.commit()
                            print(f"Música '{musica.nome}' associada ao artista '{artista.nome}' com sucesso!")
                    else:
                        print("Artista não encontrado.")

                session.commit()
                print("Música atualizada com sucesso!")
            else:
                print("Música não encontrada.")

        else:
            print("Opção inválida.")

# Função para excluir informações no banco de dados
def delete_info(session):
    if is_database_empty(session):
        print("Nenhuma informação disponível.")
    else:
        print("Escolha a opção para excluir:")
        print("1. Excluir Artista")
        print("2. Excluir Álbum")
        print("3. Excluir Gênero")
        print("4. Excluir Música")

        choice = input("Digite sua escolha: ")

        if choice == '1':
            # Excluir Artista
            show_artista(session)
            artista_id = input("Digite o ID do artista que deseja excluir: ")
            artista = session.get(Artista, artista_id)
            if artista:
                session.delete(artista)
                session.commit()
                print("Artista excluído com sucesso!")
            else:
                print("Artista não encontrado.")

        elif choice == '2':
            # Excluir Álbum
            show_album(session)
            album_id = input("Digite o ID do álbum que deseja excluir: ")
            album = session.get(Album, album_id)
            if album:
                session.delete(album)
                session.commit()
                print("Álbum excluído com sucesso!")
            else:
                print("Álbum não encontrado.")

        elif choice == '3':
            # Excluir Gênero
            show_genero(session)
            genero_id = input("Digite o ID do gênero que deseja excluir: ")
            genero = session.get(Genero, genero_id)
            if genero:
                session.delete(genero)
                session.commit()
                print("Gênero excluído com sucesso!")
            else:
                print("Gênero não encontrado.")

        elif choice == '4':
            # Excluir Música
            show_musica(session)
            musica_id = input("Digite o ID da música que deseja excluir: ")
            musica = session.get(Musica, musica_id)
            if musica:
                session.delete(musica)
                session.commit()
                print("Música excluída com sucesso!")
            else:
                print("Música não encontrada.")

        else:
            print("Opção inválida.")

# Função principal para interação
def main():
    engine = setup_database()
    session = start_session(engine)

    while True:
        print("\nMenu Principal")
        print("1. Mostrar o acervo")
        print("2. Fazer cadastro")
        print("3. Atualizar informações")
        print("4. Excluir informações")
        print("5. Sair\n")
        choice = input("Escolha uma opção: ")

        if choice == '1':
            print("\n")
            print("=" * 30)
            print("1. Ver todo o acervo")
            print("2. Apenas os Gêneros")
            print("3. Apenas os Artistas")
            print("4. Apenas os Álbuns")
            print("5. Apenas as Músicas\n")
            sub_choice = input("Escolha uma opção: ")

            if sub_choice == '1':
                show_acervo(session)
            elif sub_choice == '2':
                show_genero(session)
            elif sub_choice == '3':
                show_artista(session)
            elif sub_choice == '4':
                show_album(session)
            elif sub_choice == '5':
                show_musica(session)

        elif choice == '2':
            print("=" * 30)
            print("1. Cadastrar Gênero")
            print("2. Cadastrar Artista")
            print("3. Cadastrar Álbum")
            print("4. Cadastrar Música\n")
            sub_choice = input("Escolha uma opção: ")
            if sub_choice == '1':
                create_genero(session)
            elif sub_choice == '2':
                create_artista(session)
            elif sub_choice == '3':
                create_album(session)
            elif sub_choice == '4':
                create_musica(session)

        elif choice == '3':
            update_info(session)

        elif choice == '4':
            delete_info(session)

        elif choice == '5':
            print("Saindo...")
            break

main()