"""
PCEBG - Problema de Corte Bidimensional Guilhotinado
Algoritmo GRASP Simplificado
"""
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class Item:
    def __init__(self, id, c, l, d):
        self.id, self.c, self.l, self.d = id, c, l, d
        self.area = c * l

def criar_faixa(itens, demanda, S_c, S_l, alpha=0.8):
    """Cria uma faixa guilhotinada preenchendo ao máximo"""
    faixa = []
    x_usado = 0
    
    while x_usado < S_c:
        # Filtra itens viáveis no espaço restante
        viaveis = [i for i in itens if demanda[i.id] > 0 and 
                   i.c <= (S_c - x_usado) and i.l <= S_l]
        if not viaveis: break
        
        # LRC - prefere itens maiores
        areas = [i.area for i in viaveis]
        beta = max(areas)
        LRC = [i for i in viaveis if i.area >= alpha * beta]
        
        # Escolhe item
        item = random.choice(LRC)
        qtd = min(demanda[item.id], int((S_c - x_usado) / item.c))
        
        if qtd > 0:
            faixa.append((item, qtd, x_usado))
            demanda[item.id] -= qtd
            x_usado += qtd * item.c
    
    return faixa

def gerar_padrao(itens, demanda, C, L, alpha=0.8):
    """Gera um padrão de corte completo preenchendo ao máximo"""
    padrao = []
    y = 0
    
    while y < L and any(demanda[i.id] > 0 for i in itens):
        # Cria faixa horizontal preenchendo ao máximo
        faixa = criar_faixa(itens, demanda, C, L - y, alpha)
        if not faixa: break
        
        # Encontra altura máxima da faixa
        h_faixa = max(item.l for item, _, _ in faixa)
        
        # Adiciona itens ao padrão
        for item, qtd, x in faixa:
            padrao.append((item, qtd, x, y))
        
        y += h_faixa
    
    return padrao

def resolver_pcebg(itens, C, L, max_iter=50, alpha=0.9):
    """Resolve PCEBG com GRASP - busca mínimo desperdício"""
    melhor_sol, melhor_placas = None, float('inf')
    melhor_aproveitamento = 0
    
    for iteracao in range(max_iter):
        demanda = {i.id: i.d for i in itens}
        placas = []
        
        # Gera placas até atender demanda
        while any(demanda[i.id] > 0 for i in itens):
            padrao = gerar_padrao(itens, demanda, C, L, alpha)
            if padrao: 
                placas.append(padrao)
            else: 
                break
        
        # Calcula aproveitamento
        area_itens = sum(i.area * i.d for i in itens)
        area_placas = len(placas) * C * L
        aproveitamento = area_itens / area_placas if area_placas > 0 else 0
        
        # Atualiza melhor solução (prioriza aproveitamento, depois número de placas)
        if aproveitamento > melhor_aproveitamento or (aproveitamento == melhor_aproveitamento and len(placas) < melhor_placas):
            melhor_placas = len(placas)
            melhor_sol = placas
            melhor_aproveitamento = aproveitamento
            print(f"Iteracao {iteracao+1}: {len(placas)} placas, {aproveitamento*100:.2f}% aproveitamento")
    
    return melhor_sol

def desenhar_solucao(placas, C, L):
    """Desenha a solução"""
    n = len(placas)
    fig, axes = plt.subplots(1, min(n, 3), figsize=(5*min(n,3), 4))
    if n == 1: axes = [axes]
    
    cores = ['lightblue', 'lightgreen', 'yellow', 'lightcoral', 'plum']
    
    for idx, padrao in enumerate(placas[:3]):
        ax = axes[idx] if n > 1 else axes[0]
        ax.add_patch(patches.Rectangle((0,0), C, L, fill=False, ec='black', lw=2))
        
        for item, qtd, x, y in padrao:
            for i in range(qtd):
                cor = cores[item.id % len(cores)]
                ax.add_patch(patches.Rectangle((x + i*item.c, y), item.c, item.l, 
                            fill=True, fc=cor, ec='black'))
                ax.text(x + i*item.c + item.c/2, y + item.l/2, f'{item.id}', 
                       ha='center', va='center', fontsize=10, weight='bold')
        
        ax.set_xlim(0, C)
        ax.set_ylim(0, L)
        ax.set_aspect('equal')
        ax.set_title(f'Placa {idx+1}')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('solucao.png', dpi=200, bbox_inches='tight')
    plt.show()

# ============= EXEMPLO DE USO =============

# Exemplo com ZERO desperdício (planejado)
# Placa 10x10, itens que encaixam perfeitamente
itens = [
    Item(1, 5, 5, 2),   # 2 itens de 5x5 = 50 de área
    Item(2, 5, 4, 3),   # 5 itens de 5x2 = 50 de área
]

C, L = 5, 5  # Placa 10x10 = 100 de área total
# Total itens: 50 + 50 = 100 → aproveitamento 100%!

print("="*50)
print("EXEMPLO: Buscando solucao com minimo desperdicio")
print("="*50)

# Resolve
random.seed(42)
solucao = resolver_pcebg(itens, C, L, max_iter=50, alpha=0.95)

# Resultados
print(f"\n{'='*50}")
print("RESULTADO FINAL")
print("="*50)
print(f"[OK] Placas necessarias: {len(solucao)}")

area_itens = sum(i.area * i.d for i in itens)
area_placas = len(solucao) * C * L
aproveitamento = area_itens / area_placas * 100

print(f"[OK] Aproveitamento: {aproveitamento:.2f}%")
print(f"[OK] Desperdicio: {100-aproveitamento:.2f}%")

if aproveitamento == 100:
    print("\n*** SUCESSO! Aproveitamento perfeito (0% desperdicio) ***")
elif aproveitamento >= 95:
    print(f"\n*** EXCELENTE! Apenas {100-aproveitamento:.2f}% de desperdicio ***")
elif aproveitamento >= 85:
    print(f"\n*** BOM! Desperdicio de {100-aproveitamento:.2f}% ***")

# Desenha
print("\nGerando visualizacao...")
desenhar_solucao(solucao, C, L)
print("[OK] Imagem salva como 'solucao.png'")

print("\n" + "="*50)
print("Dica: Para melhorar o aproveitamento:")
print("- Use itens com dimensoes que dividam a placa")
print("- Aumente max_iter (ex: 100)")
print("- Aumente alpha para 0.95-0.99 (mais guloso)")
print("="*50)