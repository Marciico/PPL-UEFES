import pygame
import random
import time
import sys
import json
from pygame import mixer
from datetime import datetime

# Inicialização do Pygame
pygame.init()
mixer.init()

# Constantes
LARGURA = 800
ALTURA = 600
FPS = 60
COR_FUNDO = (0, 0, 0)
COR_ALVO = (255, 0, 0)
COR_TEXTO = (255, 255, 255)
TAMANHO_ALVO = 50
TEMPO_ALVO = 2000  # 2 segundos em milissegundos
NIVEIS_DIFICULDADE = {
    "Padawan": {"tempo": 2000, "pontos_base": 100},
    "Cavaleiro": {"tempo": 1500, "pontos_base": 150},
    "Mestre": {"tempo": 1000, "pontos_base": 200}
}

class GerenciadorSons:
    """Classe responsável por gerenciar todos os efeitos sonoros do jogo."""
    
    def __init__(self):
        """Inicializa o gerenciador de sons e carrega os arquivos de áudio."""
        self.sons = {
            "acerto": mixer.Sound("sounds/acerto.wav"),
            "erro": mixer.Sound("sounds/erro.wav"),
            "nivel_up": mixer.Sound("sounds/nivel_up.wav"),
            "game_over": mixer.Sound("sounds/game_over.wav")
        }
        
    def tocar(self, nome_som):
        """Toca um efeito sonoro específico.
        
        Args:
            nome_som (str): Nome do efeito sonoro a ser tocado.
        """
        if nome_som in self.sons:
            self.sons[nome_som].play()

class ReflexTrainer:
    """Classe principal do jogo Jedi Reflex Trainer.
    
    Esta classe gerencia todo o funcionamento do jogo, incluindo:
    - Interface do usuário
    - Lógica do jogo
    - Sistema de pontuação
    - Gerenciamento de níveis
    """
    
    def __init__(self):
        """Inicializa o jogo com suas configurações básicas."""
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Jedi Reflex Trainer")
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.Font(None, 36)
        self.fonte_grande = pygame.font.Font(None, 72)
        
        # Estado do jogo
        self.estado = "inicio"  # inicio, jogando, fim
        self.pontuacao = 0
        self.acertos = 0
        self.tempos_reacao = []
        self.alvo_atual = None
        self.tempo_alvo = 0
        self.nivel_atual = "Padawan"
        self.recordes = self.carregar_recordes()
        
        # Gerenciador de sons
        self.sons = GerenciadorSons()
        
    def carregar_recordes(self):
        """Carrega os recordes salvos do arquivo JSON.
        
        Returns:
            dict: Dicionário com os recordes carregados.
        """
        try:
            with open("recordes.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"Padawan": 0, "Cavaleiro": 0, "Mestre": 0}
            
    def salvar_recordes(self):
        """Salva os recordes atuais no arquivo JSON."""
        with open("recordes.json", "w") as f:
            json.dump(self.recordes, f)
        
    def desenhar_tela_inicio(self):
        """Desenha a tela inicial do jogo com instruções e recordes."""
        self.tela.fill(COR_FUNDO)
        
        # Título
        titulo = self.fonte_grande.render("Jedi Reflex Trainer", True, COR_TEXTO)
        self.tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, ALTURA//4))
        
        # Instruções
        instrucoes = [
            "Pressione ESPAÇO para começar",
            "Clique nos alvos vermelhos o mais rápido possível",
            "Dificuldade aumenta conforme seus acertos",
            f"Nível atual: {self.nivel_atual}"
        ]
        
        for i, texto in enumerate(instrucoes):
            render = self.fonte.render(texto, True, COR_TEXTO)
            self.tela.blit(render, (LARGURA//2 - render.get_width()//2, 
                                  ALTURA//2 + i * 40))
        
        # Recordes
        recordes_texto = self.fonte.render("Recordes:", True, COR_TEXTO)
        self.tela.blit(recordes_texto, (LARGURA//2 - recordes_texto.get_width()//2, 
                                      ALTURA - 150))
        
        for i, (nivel, recorde) in enumerate(self.recordes.items()):
            texto = self.fonte.render(f"{nivel}: {recorde} pontos", True, COR_TEXTO)
            self.tela.blit(texto, (LARGURA//2 - texto.get_width()//2, 
                                 ALTURA - 100 + i * 30))
        
    def desenhar_tela_jogo(self):
        """Desenha a tela principal do jogo com o alvo e informações."""
        self.tela.fill(COR_FUNDO)
        
        # Desenha o alvo com efeito de brilho
        if self.alvo_atual:
            pygame.draw.circle(self.tela, COR_ALVO, self.alvo_atual, TAMANHO_ALVO)
            pygame.draw.circle(self.tela, (255, 100, 100), self.alvo_atual, 
                             TAMANHO_ALVO + 5, 2)
        
        # Informações do jogo
        textos = [
            f"Pontuação: {self.pontuacao}",
            f"Nível: {self.nivel_atual}",
            f"Acertos: {self.acertos}/10"
        ]
        
        for i, texto in enumerate(textos):
            render = self.fonte.render(texto, True, COR_TEXTO)
            self.tela.blit(render, (10, 10 + i * 30))
            
        # Barra de tempo
        if self.alvo_atual:
            tempo_restante = max(0, NIVEIS_DIFICULDADE[self.nivel_atual]["tempo"] - 
                               (pygame.time.get_ticks() - self.tempo_alvo))
            largura_barra = (tempo_restante / NIVEIS_DIFICULDADE[self.nivel_atual]["tempo"]) * 200
            pygame.draw.rect(self.tela, (255, 255, 255), (LARGURA - 210, 10, 200, 20))
            pygame.draw.rect(self.tela, (0, 255, 0), (LARGURA - 210, 10, largura_barra, 20))
        
    def desenhar_tela_fim(self):
        """Desenha a tela de resultados com estatísticas e recordes."""
        self.tela.fill(COR_FUNDO)
        
        # Título
        fim_texto = self.fonte_grande.render("Fim do Treinamento!", True, COR_TEXTO)
        self.tela.blit(fim_texto, (LARGURA//2 - fim_texto.get_width()//2, ALTURA//6))
        
        # Estatísticas
        tempo_medio = sum(self.tempos_reacao) / len(self.tempos_reacao) if self.tempos_reacao else 0
        estatisticas = [
            f"Pontuação Final: {self.pontuacao}",
            f"Acertos: {self.acertos}/10",
            f"Tempo Médio de Reação: {tempo_medio:.2f}s",
            f"Nível Alcançado: {self.nivel_atual}"
        ]
        
        for i, texto in enumerate(estatisticas):
            render = self.fonte.render(texto, True, COR_TEXTO)
            self.tela.blit(render, (LARGURA//2 - render.get_width()//2, 
                                  ALTURA//3 + i * 40))
        
        # Recordes
        if self.pontuacao > self.recordes[self.nivel_atual]:
            self.recordes[self.nivel_atual] = self.pontuacao
            self.salvar_recordes()
            novo_recorde = self.fonte.render("Novo Recorde!", True, (255, 215, 0))
            self.tela.blit(novo_recorde, (LARGURA//2 - novo_recorde.get_width()//2, 
                                        ALTURA - 100))
        
        # Instruções
        continuar = self.fonte.render("Pressione ESPAÇO para jogar novamente", True, COR_TEXTO)
        self.tela.blit(continuar, (LARGURA//2 - continuar.get_width()//2, 
                                 ALTURA - 50))
        
    def gerar_alvo(self):
        """Gera um novo alvo em posição aleatória na tela."""
        x = random.randint(TAMANHO_ALVO, LARGURA - TAMANHO_ALVO)
        y = random.randint(TAMANHO_ALVO, ALTURA - TAMANHO_ALVO)
        self.alvo_atual = (x, y)
        self.tempo_alvo = pygame.time.get_ticks()
        
    def verificar_clique(self, pos):
        """Verifica se o clique do jogador acertou o alvo.
        
        Args:
            pos (tuple): Posição (x, y) do clique do mouse.
            
        Returns:
            bool: True se o clique acertou o alvo, False caso contrário.
        """
        if not self.alvo_atual:
            return False
            
        distancia = ((pos[0] - self.alvo_atual[0])**2 + 
                    (pos[1] - self.alvo_atual[1])**2)**0.5
        return distancia <= TAMANHO_ALVO
        
    def atualizar_nivel(self):
        """Atualiza o nível de dificuldade baseado na pontuação."""
        if self.pontuacao >= 1000 and self.nivel_atual == "Padawan":
            self.nivel_atual = "Cavaleiro"
            self.sons.tocar("nivel_up")
        elif self.pontuacao >= 2000 and self.nivel_atual == "Cavaleiro":
            self.nivel_atual = "Mestre"
            self.sons.tocar("nivel_up")
        
    def executar(self):
        """Loop principal do jogo."""
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        if self.estado == "inicio":
                            self.estado = "jogando"
                            self.gerar_alvo()
                        elif self.estado == "fim":
                            self.__init__()  # Reinicia o jogo
                            
                if evento.type == pygame.MOUSEBUTTONDOWN and self.estado == "jogando":
                    if self.verificar_clique(evento.pos):
                        self.sons.tocar("acerto")
                        tempo_reacao = (pygame.time.get_ticks() - self.tempo_alvo) / 1000
                        self.tempos_reacao.append(tempo_reacao)
                        pontos_base = NIVEIS_DIFICULDADE[self.nivel_atual]["pontos_base"]
                        self.pontuacao += max(pontos_base - int(tempo_reacao * 10), 10)
                        self.acertos += 1
                        self.atualizar_nivel()
                        self.gerar_alvo()
                    else:
                        self.sons.tocar("erro")
                        self.pontuacao = max(0, self.pontuacao - 5)
                        
            if self.estado == "jogando":
                tempo_atual = pygame.time.get_ticks()
                if tempo_atual - self.tempo_alvo > NIVEIS_DIFICULDADE[self.nivel_atual]["tempo"]:
                    self.alvo_atual = None
                    if len(self.tempos_reacao) >= 10:
                        self.estado = "fim"
                        self.sons.tocar("game_over")
                    else:
                        self.gerar_alvo()
                        
            if self.estado == "inicio":
                self.desenhar_tela_inicio()
            elif self.estado == "jogando":
                self.desenhar_tela_jogo()
            else:
                self.desenhar_tela_fim()
                
            pygame.display.flip()
            self.relogio.tick(FPS)

if __name__ == "__main__":
    jogo = ReflexTrainer()
    jogo.executar() 