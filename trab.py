import random
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class Item:
    def __init__(self, id, largura, altura, demanda):
        self.id = id          # identificador
        self.c = largura      # comprimento na direção horizontal (eixo x)
        self.l = altura       # altura na direção vertical (eixo y)
        self.d = demanda      # demanda total desse tipo
        self.area = largura * altura


def criar_faixa(itens, demanda, C, altura_restante, alpha=0.8):
    """
    Cria uma faixa guilhotinada horizontal preenchendo ao máximo
    o comprimento C, usando regra gulosa randomizada (LRC).
    """
    faixa = []
    x_usado = 0

    while x_usado < C:
        # Itens que ainda têm demanda e cabem no espaço restante da faixa
        viaveis = [
            i for i in itens
            if demanda[i.id] > 0 and i.c <= (C - x_usado) and i.l <= altura_restante
        ]
        if not viaveis:
            break

        # Critério guloso: maior área
        areas = [i.area for i in viaveis]
        beta = max(areas)

        # LRC: itens com área acima de alpha * beta
        LRC = [i for i in viaveis if i.area >= alpha * beta]

        # Escolhe aleatoriamente dentro da LRC
        item = random.choice(LRC)

        # Quantidade máxima que cabe na faixa, respeitando a demanda
        qtd_max = (C - x_usado) // item.c
        qtd = min(demanda[item.id], qtd_max)

        if qtd <= 0:
            break

        faixa.append((item, qtd, x_usado))
        demanda[item.id] -= qtd
        x_usado += qtd * item.c

    return faixa


def gerar_padrao(itens, demanda, C, L, alpha=0.8):
    """
    Gera um padrão completo (uma chapa) empilhando faixas horizontais.
    """
    padrao = []
    y = 0

    while y < L and any(demanda[i.id] > 0 for i in itens):
        altura_restante = L - y
        faixa = criar_faixa(itens, demanda, C, altura_restante, alpha)

        if not faixa:
            # Não há faixa possível com a demanda restante
            break

        # Altura da faixa = maior altura entre os itens colocados
        h_faixa = max(item.l for item, _, _ in faixa)

        # Registra os itens desse padrão com coordenadas (x, y)
        for item, qtd, x in faixa:
            padrao.append((item, qtd, x, y))

        y += h_faixa

    return padrao


def resolver_pcebg(itens, C, L, max_iter=50,
                   alpha_min=0.6, alpha_max=0.95,
                   verbose=False):
    """
    Resolve o PCEBG com uma versão construtiva do GRASP:
    - Em cada iteração:
        * embaralha a ordem dos itens;
        * sorteia um alpha em [alpha_min, alpha_max];
        * gera chapas até atender a demanda;
    - Ao final, retorna a melhor solução (maior aproveitamento).
    """
    melhor_solucao = None
    melhor_num_placas = math.inf
    melhor_aproveitamento = 0.0

    # Área total dos itens (fixa para todas as iterações)
    area_total_itens = sum(i.area * i.d for i in itens)

    for it in range(max_iter):
        # Copia da demanda original
        demanda = {i.id: i.d for i in itens}

        # Embaralha a ordem dos itens nesta iteração
        itens_iter = itens[:]
        random.shuffle(itens_iter)

        # Sorteia alpha para esta iteração (mais ou menos guloso)
        alpha_iter = random.uniform(alpha_min, alpha_max)

        placas = []

        # Gera chapas até atender toda a demanda
        while any(demanda[i.id] > 0 for i in itens_iter):
            padrao = gerar_padrao(itens_iter, demanda, C, L, alpha_iter)

            if not padrao:
                raise ValueError(
                    "Instância inviável: algum item não cabe na chapa padrão."
                )

            placas.append(padrao)

        # Calcula aproveitamento desta iteração
        area_placas = len(placas) * C * L
        aproveitamento = area_total_itens / area_placas if area_placas > 0 else 0.0

        if verbose:
            print(
                f"Iteração {it+1}: {len(placas)} chapas, "
                f"aproveitamento = {aproveitamento*100:.2f}% "
                f"(alpha = {alpha_iter:.2f})"
            )

        # Atualiza melhor solução
        if (aproveitamento > melhor_aproveitamento or
            (math.isclose(aproveitamento, melhor_aproveitamento)
             and len(placas) < melhor_num_placas)):
            melhor_aproveitamento = aproveitamento
            melhor_num_placas = len(placas)
            melhor_solucao = placas

    return melhor_solucao, melhor_aproveitamento


def desenhar_solucao(placas, C, L, nome_arquivo='solucao.png'):
    """
    Desenha todas as chapas da solução em um grid (até 3 colunas por linha).
    """
    n = len(placas)
    if n == 0:
        print("Nenhuma placa para desenhar.")
        return

    max_cols = 3                 # no máximo 3 colunas
    cols = min(max_cols, n)
    rows = math.ceil(n / cols)   # quantidade de linhas necessária

    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))

    # Normaliza axes para uma lista 1D
    if rows == 1 and cols == 1:
        axes = [axes]
    elif rows == 1 or cols == 1:
        axes = list(axes)
    else:
        axes = axes.ravel().tolist()

    cores = ['lightblue', 'lightgreen', 'khaki',
             'lightcoral', 'plum', 'lightsalmon']

    # Desenha cada placa
    for idx, padrao in enumerate(placas):
        ax = axes[idx]
        # Contorno da chapa
        ax.add_patch(patches.Rectangle((0, 0), C, L,
                                       fill=False, ec='black', lw=2))

        # Itens da chapa
        for item, qtd, x, y in padrao:
            for j in range(qtd):
                cor = cores[item.id % len(cores)]
                ax.add_patch(
                    patches.Rectangle(
                        (x + j * item.c, y),
                        item.c,
                        item.l,
                        fill=True,
                        fc=cor,
                        ec='black'
                    )
                )
                ax.text(
                    x + j * item.c + item.c / 2,
                    y + item.l / 2,
                    str(item.id),
                    ha='center',
                    va='center',
                    fontsize=9,
                    weight='bold'
                )

        ax.set_xlim(0, C)
        ax.set_ylim(0, L)
        ax.set_aspect('equal')
        ax.set_title(f'Placa {idx+1}')
        ax.grid(True, alpha=0.3)

    # Esconde eixos sobrando (se tiver mais "quadrinhos" do que placas)
    for k in range(n, len(axes)):
        axes[k].axis('off')

    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=200, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    # Instância usada nos seus testes (gera 6 ou 7 chapas em algumas iterações)
    itens = [
        Item(1, 8, 8, 2),   # área 64, demanda 2
        Item(2, 6, 10, 5),  # área 60, demanda 5
        Item(3, 8, 6, 5),   # área 48, demanda 5
        Item(4, 7, 5, 6),   # área 35, demanda 6
        Item(5, 4, 6, 3),   # área 24, demanda 3
    ]

    C, L = 20, 10   # Dimensões da chapa padrão (20x10 = 200 de área)

    # Comente a linha abaixo se quiser resultados diferentes a cada execução
    random.seed(42)

    solucao, aproveitamento = resolver_pcebg(
        itens,
        C,
        L,
        max_iter=20,
        alpha_min=0.6,
        alpha_max=0.95,
        verbose=True
    )

    print("\nRESULTADO FINAL")
    print(f"Chapas necessárias: {len(solucao)}")
    print(f"Aproveitamento: {aproveitamento*100:.2f}%")
    print(f"Desperdício: {(1 - aproveitamento) * 100:.2f}%")

    desenhar_solucao(solucao, C, L, nome_arquivo='solucao.png')
    print("Imagem salva como 'solucao.png'.")
