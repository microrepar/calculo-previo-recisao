import calendar
import datetime
import math

import pandas as pd
import streamlit as st

# ## Dados de entrada

# In[2]:
QTDE_DIAS_MES = 30

st.title('CÁLCULO PRÉVIO DE RESCISÃO')
EMPRESA = st.text_input('Empresa:')
FUNCIONARIO = st.text_input('Funcionário')

MOTIVO_OPTIONS = {
    'DISPENSA_DO_EMPREGADO_SEM_JUSTA_CAUSA': 1,
    'PEDIDO_DE_DEMISSÃO_POR_INICIATIVA_DO_EMPREGADO': 2,
    'TÉRMINO_DE_CONTRATO_DE_TRABALHO_A_TERMO': 3,
}

AVISO_PREVIO_OPTIONS = {
    'INDENIZADO': 1,
    'TRABALHADO': 2,
    'NAO_TRABALHADO': 3,
}

FERIAS_VENCIDAS_OPTIONS = {
    'NAO': 1,
    'SIM': 2,
    'EM_DOBRO': 3,
}

motivo_selecionado = st.radio('Motivo:', MOTIVO_OPTIONS.keys(), index=0)
st.divider()

MOTIVO = MOTIVO_OPTIONS[motivo_selecionado]

col = st.columns([.8, .8, 1.1, 1.1, 1.2])

with col[0]:
    DATA_ADMISSAO = st.date_input('Admissão', format='DD/MM/YYYY', value=datetime.datetime.strptime('01/01/2019', '%d/%m/%Y').date())
with col[1]:
    DATA_DEMISSAO = st.date_input('Demissão', format='DD/MM/YYYY', value=datetime.datetime.strptime('30/04/2020', '%d/%m/%Y').date())

with col[2]:
    SALARIO_BASE = st.number_input('Salário base', step=50., format='%.2f', value=2_500.0)

with col[3]:
    MEDIAS_HORA_EXTRA = st.number_input('Médias hora extra', step=1., format='%.2f', value=0.0)

with col[4]:
    aviso_previo_selected = st.selectbox('Aviso prévio', AVISO_PREVIO_OPTIONS.keys(), index=0)

AVISO_PREVIO = AVISO_PREVIO_OPTIONS[aviso_previo_selected]


col = st.columns([1.3, .8, .8, .8, 1, .5])

with col[0]:
    ferias_vencidas_selected = st.selectbox('Férias vencidas', FERIAS_VENCIDAS_OPTIONS.keys(), index=0)
FERIAS_VENCIDAS = FERIAS_VENCIDAS_OPTIONS[ferias_vencidas_selected]

with col[1]:
    HORAS_EXTRAS_PERCENTUAL = st.number_input('% H.E.', step=1, value=50)

with col[2]:
    HORAS_EXTRAS_QUANTIDADE = st.number_input('Qtde. H.E.', step=.1, format='%.2f', value=0.0)

with col[3]:
    HORA_EXTRA_100 = st.number_input('H.E. 100%', step=.1, format='%.2f', value=0.0)

with col[4]:
    ATRASOS_FALTAS = st.number_input('Atrasos/Faltas', step=.1, format='%.2f', value=0.0)

with col[5]:
    DEPENDENTES = st.number_input('Depend.', step=1, value=0)


# ### Tabela contribuição INSS

# In[3]:


TABELA_INSS = {
    1: (7.5/100, 1_320.01, 0.00),
    2: (9/100, 2_571.30, 18.18),
    3: (12/100, 3_856.95, 91.01),
    4: (14/100, 7_507.50, 163.00),
    5: (14/100, 7_507.50, 163.00),
}


def get_percentual_contribuicao_inss(valor_base: float):
    if valor_base <= TABELA_INSS[1][1]:
        return TABELA_INSS[1][0]
    elif valor_base <= TABELA_INSS[2][1]:
        return TABELA_INSS[2][0]
    elif valor_base <= TABELA_INSS[3][1]:
        return TABELA_INSS[3][0]
    elif valor_base <= TABELA_INSS[4][1]-0.01:
        return TABELA_INSS[4][0]
    else:
        return TABELA_INSS[5][0]
    

def get_valor_contribuicao_inss(valor_base: float):
    percentual_contribuicao = get_percentual_contribuicao_inss(valor_base)
    if valor_base > TABELA_INSS[5][1]-0.01:
        result = ((TABELA_INSS[5][1]-0.01) * percentual_contribuicao) - TABELA_INSS[5][2]
    else:
        result = valor_base * percentual_contribuicao
    
    return round(result, 2)

# ### Tabela de dedução IRRF

# In[4]:


TABELA_IRRF = {
    1: (0/100, 2_112.00, 0.0),
    2: (7.5/100, 2_826.65, 158.40),
    3: (15/100, 3_751.05, 370.40),
    4: (22.5/100, 4_664.68, 651.73),
    5: (27.5/100, 4_664.69, 884.96),
    6: ('DEDUÇÃO/DEPENDENTE', 189.59),
}

def get_percentual_irrf(valor_base):
    if valor_base <= TABELA_IRRF[1][1]:
        return TABELA_IRRF[1][0]
    elif valor_base <= TABELA_IRRF[2][1]:
        return TABELA_IRRF[2][0]
    elif valor_base <= TABELA_IRRF[3][1]:
        return TABELA_IRRF[3][0]
    elif valor_base <= TABELA_IRRF[4][1]:
        return TABELA_IRRF[4][0]
    else:
        return TABELA_IRRF[5][0]

def get_deducao_irrf(valor_base):
    if valor_base <= TABELA_IRRF[1][1]:
        return TABELA_IRRF[1][2]
    elif valor_base <= TABELA_IRRF[2][1]:
        return TABELA_IRRF[2][2]
    elif valor_base <= TABELA_IRRF[3][1]:
        return TABELA_IRRF[3][2]
    elif valor_base <= TABELA_IRRF[4][1]:
        return TABELA_IRRF[4][2]
    else:
        return TABELA_IRRF[5][2]

# ### TABELA DE SEGURO DESEMPREGO

# In[5]:


TABELA_SEGURO_DESEMPREGO = {
    1: {'percentual': 80/100, 'valor': 1_968.37},
    2: {'percentual': 50/100, 'valor': 3_280.93},
    'FIXO': {'fixo': 2_230.97, 'valor': 3_280.94},
    'MINIMO_VIGENTE': 1_320.00,
}

def get_valor_por_parcela_seg(valor_base):
    valor_parcial1 = 0.0
    valor_parcial2 = 0.0
    valor_tabela_calculo = 0.0

    if valor_base < TABELA_SEGURO_DESEMPREGO[1]['valor']:
        valor_tabela_calculo = valor_base 
    else:
        valor_tabela_calculo = TABELA_SEGURO_DESEMPREGO[1]['valor']
    valor_parcial1 = valor_tabela_calculo * TABELA_SEGURO_DESEMPREGO[1]['percentual']

    if valor_tabela_calculo == TABELA_SEGURO_DESEMPREGO[1]['valor']:
        valor_parcial2 = valor_base - TABELA_SEGURO_DESEMPREGO[1]['valor']
    valor_parcial2 = valor_parcial2 * TABELA_SEGURO_DESEMPREGO[2]['percentual']
    
    total_parcial = valor_parcial1 + valor_parcial2

    if TABELA_SEGURO_DESEMPREGO['MINIMO_VIGENTE'] > total_parcial:
        resultado_parcial = TABELA_SEGURO_DESEMPREGO['MINIMO_VIGENTE']
    else:
        resultado_parcial = total_parcial

    if valor_base >= TABELA_SEGURO_DESEMPREGO['FIXO']['valor']:
        resultado = TABELA_SEGURO_DESEMPREGO['FIXO']['fixo']
    else:
        resultado = resultado_parcial

    return round(resultado, 2)

# ### Datas

# In[6]:


DIA_ADMISSAO = DATA_ADMISSAO.day
MES_ADMISSAO = DATA_ADMISSAO.month
ANO_ADMISSAO = DATA_ADMISSAO.year

DIA_DEMISSAO = DATA_DEMISSAO.day
MES_DEMISSAO = DATA_DEMISSAO.month
ANO_DEMISSAO = DATA_DEMISSAO.year

# ## Proventos

# In[7]:


lista_vencimentos = []
campo1_adicional_qtde = 0
campo2_adicional_qtde = 0
campo1_adicional_valor = 0
campo2_adicional_valor = 0

lista_vencimentos.append(campo1_adicional_valor)
lista_vencimentos.append(campo2_adicional_valor)

# In[8]:



def get_saldo_salario_quantidade():
    mes_ano_admissao = f'{MES_ADMISSAO:0>2}/{ANO_ADMISSAO}'
    mes_ano_demissao = f'{MES_DEMISSAO:0>2}/{ANO_DEMISSAO}'

    mesmo_mes_ano_admissao_demissao = True if mes_ano_admissao == mes_ano_demissao else False

    if mesmo_mes_ano_admissao_demissao:
        quantidade_de_dias = DIA_DEMISSAO - DIA_ADMISSAO
        return quantidade_de_dias
    return DIA_DEMISSAO


saldo_de_salario_qtde = get_saldo_salario_quantidade()
saldo_de_salario_valor = round(SALARIO_BASE/QTDE_DIAS_MES*saldo_de_salario_qtde, 2)
lista_vencimentos.append(saldo_de_salario_valor)

# print('saldo_de_salario:', saldo_de_salario_qtde, saldo_de_salario_valor)

# In[9]:


def get_salario_proporcional_13_qtde(salario_qtde):
    mesmo_ano_admissao_demissao = True if ANO_ADMISSAO == ANO_DEMISSAO else False
    data_proporcao = None
    if mesmo_ano_admissao_demissao:
        data_proporcao = DATA_ADMISSAO
    else:
        data_proporcao = datetime.datetime.strptime(f'01/01/{ANO_DEMISSAO}', '%d/%m/%Y')

    mes_proporcao = data_proporcao.month

    mes_demissao = DATA_DEMISSAO.month
    
    if salario_qtde < 15:
        qtde_proporcional = (mes_demissao - 1) - mes_proporcao
    else:
        qtde_proporcional = mes_demissao - mes_proporcao
    
    return qtde_proporcional + 1


salario_proporcional_13_qtde = get_salario_proporcional_13_qtde(saldo_de_salario_qtde)
salario_proporcional_13_valor = (SALARIO_BASE / 12) * salario_proporcional_13_qtde
lista_vencimentos.append(salario_proporcional_13_valor)

# print('salario_proporcional_13:', f'{salario_proporcional_13_qtde}/12', f'{salario_proporcional_13_valor:.2f}')

# In[10]:


salario_variavel_13_qtde = get_salario_proporcional_13_qtde(saldo_de_salario_qtde)
salario_variavel_13_valor = round((MEDIAS_HORA_EXTRA / 12) * salario_proporcional_13_qtde, 2)
lista_vencimentos.append(salario_variavel_13_valor)

# print('salario_variavel_13:', f'{salario_variavel_13_qtde}/12', salario_variavel_13_valor)

# In[ ]:


if MOTIVO != 1 or AVISO_PREVIO != 1:
    salario_indenizado_13_qtde = 0
    salario_indenizado_13_valor = 0
else:
    salario_indenizado_13_qtde = 1
    salario_indenizado_13_valor = (SALARIO_BASE + MEDIAS_HORA_EXTRA) / 12

lista_vencimentos.append(salario_indenizado_13_valor)

# print('salario_indenizado_13', F'{salario_indenizado_13_qtde:0>2}/12', round(salario_indenizado_13_valor,2))

# In[ ]:


ferias_vencidas_qtde = None
if FERIAS_VENCIDAS == 1:
    ferias_vencidas_qtde = 0
elif FERIAS_VENCIDAS == 2:
    ferias_vencidas_qtde = 1
elif FERIAS_VENCIDAS == 3:
    ferias_vencidas_qtde = 3

ferias_vencidas_valor = (SALARIO_BASE + MEDIAS_HORA_EXTRA) * ferias_vencidas_qtde
lista_vencimentos.append(ferias_vencidas_valor)

# print('ferias_vencidas:', ferias_vencidas_qtde, ferias_vencidas_valor)

# In[ ]:


def get_ferias_proporcionais_qtde():
    
    if DIA_DEMISSAO >= 15:
        qtde_dias_mes_demissao = calendar.monthrange(DATA_DEMISSAO.year, DATA_DEMISSAO.month)[-1]
    else:
        qtde_dias_mes_demissao = 1

    data_dia_mes_admissao__ano_dem = datetime.datetime.strptime(f'{DIA_ADMISSAO}/{MES_ADMISSAO}/{ANO_DEMISSAO}', '%d/%m/%Y')
    data_qtde_dias__mes_ano_demissao = datetime.datetime.strptime(f'{qtde_dias_mes_demissao}/{MES_DEMISSAO}/{ANO_DEMISSAO}', '%d/%m/%Y')
    data_dia_mes_admissao__ano_anterior = data_dia_mes_admissao__ano_dem - datetime.timedelta(days=365)

    dia_mes_admissao_maior_que_dia_mes_demissao = data_dia_mes_admissao__ano_dem > data_qtde_dias__mes_ano_demissao

    if dia_mes_admissao_maior_que_dia_mes_demissao:
        result = data_qtde_dias__mes_ano_demissao - data_dia_mes_admissao__ano_anterior
    else:
        if (DATA_DEMISSAO - DATA_ADMISSAO).days > 365:
            result = data_qtde_dias__mes_ano_demissao - data_dia_mes_admissao__ano_dem
        else:
            result = data_qtde_dias__mes_ano_demissao - DATA_ADMISSAO

    if result.days > 14:
        if result.days <= 30:
            valor_calculo = 30
        else:
            valor_calculo = result.days
    else:
        valor_calculo = 0

    valor_calculo = (valor_calculo / 30 + 0.000001)
    valor_calculo_arredon_acima = math.ceil(valor_calculo)
    valor_calculo_arredon_abaixo = math.floor(valor_calculo)
    
    if valor_calculo_arredon_acima < (valor_calculo - valor_calculo_arredon_abaixo):
        resultado_final = valor_calculo_arredon_acima
    else:
        resultado_final = valor_calculo_arredon_abaixo
    
    return resultado_final

# In[ ]:


ferias_proporcionais_qtde = get_ferias_proporcionais_qtde()
ferias_proporcionais_valor = round((SALARIO_BASE + MEDIAS_HORA_EXTRA) / 12 * ferias_proporcionais_qtde, 2)
lista_vencimentos.append(ferias_proporcionais_valor)

# print('ferias_proporcionais:', f'{ferias_proporcionais_qtde}/12', ferias_proporcionais_valor)

# In[ ]:


ferias_indenizadas_qtde = salario_indenizado_13_qtde
ferias_indenizadas_valor = round(salario_indenizado_13_valor, 2)
lista_vencimentos.append(ferias_indenizadas_valor)

# print('ferias_indenizadas:', ferias_indenizadas_qtde, ferias_indenizadas_valor)

# In[ ]:


um_terco_sobre_ferias_qtde = '01/03'
um_terco_sobre_ferias_valor = round(sum([ferias_vencidas_valor, ferias_proporcionais_valor, ferias_indenizadas_valor]) / 3, 2)
lista_vencimentos.append(um_terco_sobre_ferias_valor)

# print('um_terco_sobre_ferias:', um_terco_sobre_ferias_qtde, um_terco_sobre_ferias_valor)

# In[ ]:


qtde_horas = int(HORAS_EXTRAS_QUANTIDADE)
qtde_minutos = (HORAS_EXTRAS_QUANTIDADE - qtde_horas) * 100
total_em_minutos = (qtde_horas * 60) + qtde_minutos
resultado_total_he = total_em_minutos / 60

horas_extras_50_valor = round(((SALARIO_BASE / 220) + ((SALARIO_BASE / 220) * HORAS_EXTRAS_PERCENTUAL)) * resultado_total_he, 2)
horas_extras_100_valor = round((SALARIO_BASE / 220) * 2 * HORA_EXTRA_100, 2)
lista_vencimentos.append(horas_extras_50_valor)
lista_vencimentos.append(horas_extras_100_valor)

# print('horas_extras_50: ', HORAS_EXTRAS_QUANTIDADE, horas_extras_50_valor)
# print('horas_extras_100:', HORA_EXTRA_100, horas_extras_100_valor)

# In[ ]:


def get_aviso_previo_inden_valor():
    salario_base_por_30 = (SALARIO_BASE / 30)
    
    salario_base_mais_medias_he = (SALARIO_BASE + MEDIAS_HORA_EXTRA)

    qtde_total_dias_registro = (DATA_DEMISSAO - DATA_ADMISSAO).days
    qtde_anos_resgistro = qtde_total_dias_registro / 365
    qtde_anos_arredondado_acima = math.floor(qtde_anos_resgistro)
    
    result = (salario_base_por_30 * (qtde_anos_arredondado_acima * 3)) + salario_base_mais_medias_he
    return result

# In[ ]:


aviso_previo_inden_qtde = 0
aviso_previo_inden_valor = 0
if AVISO_PREVIO == 1:
    aviso_previo_inden_qtde = 1
    aviso_previo_inden_valor = get_aviso_previo_inden_valor()

lista_vencimentos.append(aviso_previo_inden_valor)

# print('aviso_previo_inden:', aviso_previo_inden_qtde, aviso_previo_inden_valor)

# In[ ]:


total_vencimentos = round(sum(lista_vencimentos), 2)

# print('total_vencimentos:', total_vencimentos)

# ## Descontos

# In[ ]:


lista_descontos = []
lista_vencimento_base_calc_inss = [
    saldo_de_salario_valor,
    horas_extras_50_valor,
    horas_extras_100_valor,
    campo1_adicional_valor,
    campo2_adicional_valor,
]

valor_base_calculo_inss = sum(lista_vencimento_base_calc_inss)
valor_base_calculo_13 = sum([salario_proporcional_13_valor, salario_variavel_13_valor])

# In[ ]:


inss_sobre_saldo_salario_qtde = get_percentual_contribuicao_inss(valor_base_calculo_inss)
inss_sobre_saldo_salario_valor = get_valor_contribuicao_inss(valor_base_calculo_inss)
lista_descontos.append(inss_sobre_saldo_salario_valor)

# print('inss_sobre_saldo_salario:', inss_sobre_saldo_salario_qtde, inss_sobre_saldo_salario_valor)

# In[ ]:


qtde_horas = int(ATRASOS_FALTAS)
qtde_minutos = (ATRASOS_FALTAS - qtde_horas) * 100
total_em_minutos = (qtde_horas * 60) + qtde_minutos
resultado_atrasos_faltas = total_em_minutos / 60

atrasos_faltas_qtde = ATRASOS_FALTAS
atrasos_faltas_valor = round(resultado_atrasos_faltas * (SALARIO_BASE / 220), 2)
lista_descontos.append(atrasos_faltas_valor)

# print('atrasos_faltas:', atrasos_faltas_qtde, atrasos_faltas_valor)

# In[ ]:


lista_vencimentos_base_calc_irrf = [
    saldo_de_salario_valor,
    horas_extras_50_valor,
    horas_extras_100_valor,
    aviso_previo_inden_valor,
    campo1_adicional_valor,
    campo2_adicional_valor,
]

lista_vencimentos_13_base_calc_irrf = [
    salario_indenizado_13_valor,
    salario_variavel_13_valor,
    salario_proporcional_13_valor,
]

valor_base_calculo_irrf = sum(lista_vencimentos_base_calc_irrf) - inss_sobre_saldo_salario_valor - atrasos_faltas_valor

if DEPENDENTES > 5 :
    valor_base_calculo_irrf_sobre_13 = sum(lista_vencimentos_13_base_calc_irrf) - (5 * TABELA_IRRF[6][1])
else:
    valor_base_calculo_irrf_sobre_13 = sum(lista_vencimentos_13_base_calc_irrf) - (DEPENDENTES * TABELA_IRRF[6][1])

# In[ ]:


inss_sobre_salario_13_qtde = get_percentual_contribuicao_inss(valor_base_calculo_13)
inss_sobre_salario_13_valor = get_valor_contribuicao_inss(valor_base_calculo_13)
lista_descontos.append(inss_sobre_salario_13_valor)

# print('inss_sobre_salario_13:', inss_sobre_salario_13_qtde, inss_sobre_salario_13_valor)

# In[ ]:


def get_valor_irrf(valor_base: float):
    resultado_parcial_irrf = valor_base * get_percentual_irrf(valor_base)
    deducao_irrf = get_deducao_irrf(valor_base)
    return round(resultado_parcial_irrf - deducao_irrf, 2)


irrf_sobre_salario_qtde = get_percentual_irrf(valor_base_calculo_irrf)
irrf_sobre_salario_valor = get_valor_irrf(valor_base_calculo_irrf)
lista_descontos.append(irrf_sobre_salario_valor)

# print('irrf_sobre_salario:', irrf_sobre_salario_qtde, irrf_sobre_salario_valor)

# In[ ]:


irrf_sobre_salario_13_qtde = get_percentual_irrf(valor_base_calculo_irrf_sobre_13)
irrf_sobre_salario_13_valor = get_valor_irrf(valor_base_calculo_irrf_sobre_13)
lista_descontos.append(irrf_sobre_salario_13_valor)

# print('irrf_sobre_salario_13:', irrf_sobre_salario_13_qtde, irrf_sobre_salario_13_valor)

# In[ ]:


desconto_aviso_previo_qtde = 0
desconto_aviso_previo_valor = 0.0

if MOTIVO == 2 and AVISO_PREVIO == 3:
    desconto_aviso_previo_qtde = 1
    desconto_aviso_previo_valor = SALARIO_BASE + MEDIAS_HORA_EXTRA

lista_descontos.append(desconto_aviso_previo_valor)

# print('desconto_aviso_previo:', desconto_aviso_previo_qtde, desconto_aviso_previo_valor)

# In[ ]:


adiantamentos_qtde = 0
adiantamentos_valor = 0.0
lista_descontos.append(adiantamentos_valor)

# In[ ]:


total_descontos = round(sum(lista_descontos), 2)


# print('total_descontos:', total_descontos)

# ### LÍQUIDO DE RECISÃO

# In[ ]:


liquido_de_rescisao = total_vencimentos - total_descontos

# print('TOTAL DE VENCIMENTOS:', total_vencimentos)
# print('TOTAL DE DESCONTOS:   ', total_descontos)
# print('LIQUÍDO DE RECISÃO:  ', liquido_de_rescisao)

##########################################################################
##########################################################################
st.divider()
col1 , col2 = st.columns(2)
col1.markdown('### PROVENTOS')
col2.markdown('### DESCONTOS')

proventos_dict = {
    'Parâmetro': [
        'SALDO DE SALÁRIO',
        '13º SALÁRIO PROP.',
        '13º SALÁRIO VARIÁVEL',
        '13º SALÁRIO INDENIZADO',
        'FÉRIAS VENCIDAS',
        'FÉRIAS PROPORCIONAIS',
        '1/3 SOBRE FÉRIAS',
        'HORA EXTRA 50%',
        'HORA EXTRA 100%',
        'AVISO PRÉVIO INDEN.',
        '-',
        '-',
        'TOTAL DE VENCIMENTOS',
        'LIQUÍDO DE RECISÃO',

    ],
    'Qtde.': [
        f'{saldo_de_salario_qtde}',
        f'{salario_proporcional_13_qtde:0>2}/12',
        f'{salario_variavel_13_qtde:0>2}/12',
        f'{salario_indenizado_13_qtde:0>2}/12',
        f'{ferias_vencidas_qtde:0>2}/12',
        f'{ferias_proporcionais_qtde:0>2}/12',
        f'{um_terco_sobre_ferias_qtde:0>2}',
        f'{HORAS_EXTRAS_QUANTIDADE}',
        f'{HORA_EXTRA_100}',
        f'{aviso_previo_inden_qtde}',
        f'{campo1_adicional_qtde}',
        f'{campo2_adicional_qtde}',
        f'{">>>>"}',
        f'{">>>>"}',

    ],
    'Valor': [
        saldo_de_salario_valor,
        salario_proporcional_13_valor,
        salario_variavel_13_valor,
        salario_indenizado_13_valor,
        ferias_vencidas_valor,
        ferias_proporcionais_valor,
        um_terco_sobre_ferias_valor,
        horas_extras_50_valor,
        horas_extras_100_valor,
        aviso_previo_inden_valor,
        campo1_adicional_valor,
        campo2_adicional_valor,
        total_vencimentos,
        liquido_de_rescisao,
    ],
}

def format_currency(value):
    return 'R$ {:,.2f}'.format(value).replace(',', '_').replace('.', ',').replace('_', '.')

df_proventos = pd.DataFrame(proventos_dict)
df_proventos['Valor'] = df_proventos['Valor'].map(format_currency)

# Função para estilizar as células do último registro
def highlight_last_row(row):
    if 'TOTAL' in row['Parâmetro'] or 'LIQU' in row['Parâmetro']:
        return ['background-color: #454545']*len(row)
    else:
        return ['']*len(row)

# Exibe o DataFrame com o estilo aplicado
styled_df = df_proventos.style.apply(highlight_last_row, axis=1)

with col1:
    st.dataframe(styled_df, hide_index=True, use_container_width=True)


descontos_dict = {
    'Parâmetro': [
        'INSS SOBRE SALDO DE SALÁRIO',
        'INSS SOBRE 13º SALÁRIO',
        'IRRF SOBRE SALÁRIO',
        'IRRF SOBRE 13º SALÁRIO',
        'AVISO PRÉVIO',
        'FALTAS / ATRASOS',
        'ADIANTAMENTOS',
        '-',
        '-',
        '-',
        '-',
        '-',
        '-',
        'TOTAL DE DESCONTOS',
    ],
    'Qtde.': [
        f'{inss_sobre_saldo_salario_qtde*100:.2f}%',
        f'{inss_sobre_salario_13_qtde*100:.2f}%',
        f'{irrf_sobre_salario_qtde*100:.2f}%',
        f'{irrf_sobre_salario_13_qtde*100:.2f}%',
        f'{desconto_aviso_previo_qtde*100:.2f}%',
        f'{atrasos_faltas_qtde}',
        f'{adiantamentos_qtde}',
        '-',
        '-',
        '-',
        '-',
        '-',
        '-',
        '>>>>',
    ],
    'Valor': [
        inss_sobre_saldo_salario_valor,
        inss_sobre_salario_13_valor,
        irrf_sobre_salario_valor,
        irrf_sobre_salario_13_valor,
        desconto_aviso_previo_valor,
        atrasos_faltas_valor,
        adiantamentos_valor,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        total_descontos,
    ],
}

df_descontos = pd.DataFrame(descontos_dict)
df_descontos['Valor'] = df_descontos['Valor'].map(format_currency)

styled_df = df_descontos.style.apply(highlight_last_row, axis=1)
with col2:
    st.dataframe(styled_df, hide_index=True, use_container_width=True)
st.divider()

# ### CÁLCULO DE MULTA DO FGTS
# In[ ]:

GRRF_OPTIONS = {
    'GRRF (CALC. 40%)': 40/100,
    'GRRF (CALC. 50%)': 50/100,
}

col1, col2 = st.columns(2)
col1.markdown('### CÁLCULO DE MULTA DO FGTS')

FGTS_DEPOSITADO = col1.number_input('FGTS DEPOSITADO', step=50., format='%.2f', value=0.0)

with col1:
    col_inner = st.columns([1.5,1])

grrf_selected = col_inner[0].selectbox('GRRF', GRRF_OPTIONS.keys(), index=1)
GRRF = GRRF_OPTIONS[grrf_selected]


# In[ ]:


lista_base_calculo_fgts_vencimento = [
    saldo_de_salario_valor,
    salario_proporcional_13_valor,
    salario_variavel_13_valor,
    horas_extras_50_valor,
    horas_extras_100_valor,
    campo1_adicional_valor,
    campo2_adicional_valor,
]

valor_base_calculo_fgts_vencimento = sum(lista_base_calculo_fgts_vencimento)

# In[ ]:


calculo_grrf = round(0.0 if MOTIVO !=1 else FGTS_DEPOSITADO * GRRF, 2)
fgts_vencimentos = round(valor_base_calculo_fgts_vencimento * (8/100), 2)
fgts_aviso_previo = round((aviso_previo_inden_valor + salario_indenizado_13_valor) * (8/100), 2)
total_conta_fgts = round(sum([FGTS_DEPOSITADO, calculo_grrf * 80/100, fgts_vencimentos, fgts_aviso_previo]), 2)


total_guia_grfc = sum([
    calculo_grrf,
    fgts_vencimentos,
    fgts_aviso_previo,
])

# print('calculo_grrf:     ', calculo_grrf)
# print('fgts_vencimentos: ', fgts_vencimentos)
# print('fgts_aviso_previo:', fgts_aviso_previo)
# print('total_conta_fgts: ', total_conta_fgts)
# print('total_guia_grfc:  ', total_guia_grfc)

col_inner[1].text_input('Cálculo GRRF', value=f'{calculo_grrf}', disabled=True)

df_fgts = pd.DataFrame(
    {
        'Parâmetro': [
            'FGTS (VENCIMENTOS)',
            'FGTS (AVISO PRÉVIO)',
            'TOTAL CONTA FGTS',
            'TOTAL GUIA GRFC:',
        ],
        'Valor': [
            fgts_vencimentos,
            fgts_aviso_previo,
            total_conta_fgts,
            total_guia_grfc,
        ],
    }
)

df_fgts['Valor'] = df_fgts['Valor'].map(format_currency)

# Exibe o DataFrame com o estilo aplicado
styled_df = df_fgts.style.apply(highlight_last_row, axis=1)

col1.dataframe(styled_df, hide_index=True, use_container_width=True)

# ### CÁLCULO DE SEGURO DESEMPREGO

# In[ ]:
col2.markdown('### CÁLCULO DE SEGURO DESEMPREGO')

MAPA_PARCELAS_SEGURO = {
    1:	0,  2:	0,  3:	0,  4:	0,  5:	0,  6:	3,  7:	3,
    8:	3,  9:	3,  10:	3,  11:	3,  12:	4,  13:	4,  14:	4,  
    15:	4,  16:	4,  17:	4,  18:	4,  19:	4,  20:	4,  21:	4,
    22:	4,  23:	4,  24:	5,  25:	5,  0:	0,}

def get_numero_parcelas():
    meses_trabalhado = (DATA_DEMISSAO - DATA_ADMISSAO).days // 30
    if meses_trabalhado > 25:
        return MAPA_PARCELAS_SEGURO[25]
    return MAPA_PARCELAS_SEGURO[meses_trabalhado]


valor_media_salarial_base_calculo = SALARIO_BASE + MEDIAS_HORA_EXTRA


# In[ ]:


media_salarial = 0.0 if MOTIVO != 1 else valor_media_salarial_base_calculo
numero_parcelas = 0 if MOTIVO != 1 else get_numero_parcelas()
valor_por_parcela = 0.0 if MOTIVO != 1 and numero_parcelas == 0 else get_valor_por_parcela_seg(valor_media_salarial_base_calculo)
total_seguro_desemprego = round(0.0 if MOTIVO != 1 else numero_parcelas * valor_por_parcela, 2)

# print('media_salarial:         ', media_salarial)
# print('numero_parcelas:        ', numero_parcelas)
# print('valor_por_parcela:      ', valor_por_parcela)
# print('total_seguro_desemprego:', total_seguro_desemprego)

df_seguro = pd.DataFrame(
    {
        'Parâmetro': [
            'MÉDIA SALARIAL',
            'PARCELAS',
            'VALOR POR PARCELA',
            'TOTAL SEGURO DESEMPREDO:'
        ],
        'Valor': [
            media_salarial,
            numero_parcelas,
            valor_por_parcela,
            total_seguro_desemprego,
        ],
    }
)

def format_currency(row):
    if row.name != 1:
        return 'R$ {:,.2f}'.format(row['Valor']).replace(',', '_').replace('.', ',').replace('_', '.')
    return int(row['Valor'])

df_seguro['Valor'] = df_seguro.apply(lambda row: format_currency(row), axis=1)

# Exibe o DataFrame com o estilo aplicado
styled_df = df_seguro.style.apply(highlight_last_row, axis=1)

col2.dataframe(styled_df, hide_index=True, use_container_width=True)

# In[ ]:
resultado_da_rescisao = sum(
    [liquido_de_rescisao, total_guia_grfc, total_seguro_desemprego]
)

# print('RESCISÃO + MULTA FGTS + SEGURO DESEMPREGO:', resultado_da_rescisao)

st.markdown(f'#### RESCISÃO + MULTA FGTS + SEGURO DESEMPREGO: R$ {resultado_da_rescisao:,.2f}')

# ## RESUMO DE CÁLCULO DE RECISÃO

# In[ ]:


total_grf_parte_funcionario = sum([calculo_grrf*80/100, fgts_vencimentos, fgts_aviso_previo])

# print('-' * 63)
# print('RESCISÃO:')
# print(f'{"VALOR LÍQUIDO DA RESCISÃO":.<50}', f'R$ {liquido_de_rescisao}')
# print()
# print('FUNDO DE GARANTIA:')
# print(f'{"TOTAL GRFC (SOMENTE A PARTE DO FUNCIONÁRIO):":.<50}', f'R$ {total_grf_parte_funcionario}')
# print(f'{"TOTAL DEPOSITADO NA CONTA DO FGTS:":.<50}', f'R$ {total_conta_fgts}')
# print()
# print('-' * 63)
# print('SEGURO DESEMPREGO (VALORES ESTIMADOS):')
# print(f'{"QUANTIDADE DE PARCELAS:":.<50}', f' {numero_parcelas}')
# print(f'{"VALOR POR PARCELA:":.<50}', f'R$ {valor_por_parcela}')
# print(f'{"TOTAL A RECEBER (SEGURO DESEMPREGO):":.<50}', f'R$ {total_seguro_desemprego}')
# print()
# print('-' * 63)
# print('VALOR TOTAL A RECEBER:')
# print(f'{"RESCISÃO":.<50}', f'R$ {liquido_de_rescisao}')
# print(f'{"MULTA FGTS:":.<50}', f'R$ {total_grf_parte_funcionario}')
# print(f'{"FGTS DEPOSITADO:":.<50}', f'R$ {FGTS_DEPOSITADO}')
# print(f'{"SEGURO DESEMPREGO:":.<50}', f'R$ {total_seguro_desemprego}')
# print('-' * 63)
TOTAL_RESUMO = sum([
    liquido_de_rescisao,
    total_grf_parte_funcionario,
    FGTS_DEPOSITADO,
    total_seguro_desemprego,
])
# print(f'{"TOTAL A RECEBER:":.<50}', f'R$ {TOTAL_RESUMO}')
