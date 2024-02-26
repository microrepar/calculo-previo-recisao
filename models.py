import calendar
import math
from typing import Optional
import datetime


class CalculoRescisao:
    TABELA_INSS = {
        1: (7.5 / 100, 1_320.01, 0.00),
        2: (9 / 100, 2_571.30, 18.18),
        3: (12 / 100, 3_856.95, 91.01),
        4: (14 / 100, 7_507.50, 163.00),
        5: (14 / 100, 7_507.50, 163.00),
    }
    TABELA_IRRF = {
        1: (0/100, 2_112.00, 0.0),
        2: (7.5/100, 2_826.65, 158.40),
        3: (15/100, 3_751.05, 370.40),
        4: (22.5/100, 4_664.68, 651.73),
        5: (27.5/100, 4_664.69, 884.96),
        6: ('DEDUÇÃO/DEPENDENTE', 189.59),
    }

    TABELA_SEGURO_DESEMPREGO = {
        1: {'percentual': 80/100, 'valor': 1_968.37},
        2: {'percentual': 50/100, 'valor': 3_280.93},
        'FIXO': {'fixo': 2_230.97, 'valor': 3_280.94},
        'MINIMO_VIGENTE': 1_320.00,
    }

    MAPA_PARCELAS_SEGURO = {
        1:	0,  2:	0,  3:	0,  4:	0,  5:	0,  6:	3,  7:	3,
        8:	3,  9:	3,  10:	3,  11:	3,  12:	4,  13:	4,  14:	4,  
        15:	4,  16:	4,  17:	4,  18:	4,  19:	4,  20:	4,  21:	4,
        22:	4,  23:	4,  24:	5,  25:	5,  0:	0,
    }

    def __init__(self,
                 qtde_dias_mes: int = 30,
                 empresa: str = '',
                 funcionario: str = '',
                 motivo: int = 1,
                 data_admissao: datetime.datetime = None,
                 data_demissao: datetime.datetime = None,
                 salario_base: float = None,
                 medias_hora_extra: float = 0.0,
                 aviso_previo: int = 1,
                 ferias_vencidas: int = 1,
                 horas_extras_percentual: float = 50/100,
                 horas_extras_quantidade: float = 0.0,
                 hora_extra_100: float = 0.0,
                 atrasos_faltas: float = 0.0,
                 dependentes: int = 0,
                 grrf: float = 0.0,
                 fgts_depositado: float = 0.0,):
      
        self.qtde_dias_mes = qtde_dias_mes
        self.empresa = empresa
        self.funcionario = funcionario
        self.motivo = motivo
        self.data_admissao = data_admissao
        self.data_demissao = data_demissao
        self.salario_base = salario_base
        self.medias_hora_extra = medias_hora_extra
        self.aviso_previo = aviso_previo
        self.ferias_vencidas = ferias_vencidas
        self.horas_extras_percentual = horas_extras_percentual
        self.horas_extras_quantidade = horas_extras_quantidade
        self.hora_extra_100 = hora_extra_100
        self.atrasos_faltas = atrasos_faltas
        self.dependentes = dependentes
        self.grrf = grrf
        self.fgts_depositado = fgts_depositado

        self.campo1_adicional_qtde = 0
        self.campo2_adicional_qtde = 0
        self.campo1_adicional_valor = 0
        self.campo2_adicional_valor = 0

        # Adicionando os novos atributos
        if data_admissao is not None:
            self.dia_admissao = data_admissao.day
            self.mes_admissao = data_admissao.month
            self.ano_admissao = data_admissao.year

        if data_demissao is not None:
            self.dia_demissao = data_demissao.day
            self.mes_demissao = data_demissao.month
            self.ano_demissao = data_demissao.year
    
    def get_percentual_contribuicao_inss(self, valor_base: float):
        if valor_base <= self.TABELA_INSS[1][1]:
            return self.TABELA_INSS[1][0]
        elif valor_base <= self.TABELA_INSS[2][1]:
            return self.TABELA_INSS[2][0]
        elif valor_base <= self.TABELA_INSS[3][1]:
            return self.TABELA_INSS[3][0]
        elif valor_base <= self.TABELA_INSS[4][1]-0.01:
            return self.TABELA_INSS[4][0]
        else:
            return self.TABELA_INSS[5][0]
        
    def get_valor_contribuicao_inss(self, valor_base: float):
        percentual_contribuicao = self.get_percentual_contribuicao_inss(valor_base)
        if valor_base > self.TABELA_INSS[5][1]-0.01:
            result = ((self.TABELA_INSS[5][1]-0.01) * percentual_contribuicao) - TABELA_INSS[5][2]
        else:
            result = valor_base * percentual_contribuicao
        
        return round(result, 2)
    
    def get_percentual_irrf(self, valor_base):
        if valor_base <= self.TABELA_IRRF[1][1]:
            return self.TABELA_IRRF[1][0]
        elif valor_base <= self.TABELA_IRRF[2][1]:
            return self.TABELA_IRRF[2][0]
        elif valor_base <= self.TABELA_IRRF[3][1]:
            return self.TABELA_IRRF[3][0]
        elif valor_base <= self.TABELA_IRRF[4][1]:
            return self.TABELA_IRRF[4][0]
        else:
            return self.TABELA_IRRF[5][0]

    def get_deducao_irrf(self, valor_base):
        if valor_base <= self.TABELA_IRRF[1][1]:
            return self.TABELA_IRRF[1][2]
        elif valor_base <= self.TABELA_IRRF[2][1]:
            return self.TABELA_IRRF[2][2]
        elif valor_base <= self.TABELA_IRRF[3][1]:
            return self.TABELA_IRRF[3][2]
        elif valor_base <= self.TABELA_IRRF[4][1]:
            return self.TABELA_IRRF[4][2]
        else:
            return self.TABELA_IRRF[5][2]

    def get_valor_por_parcela_seg(self, valor_base):
        valor_parcial1 = 0.0
        valor_parcial2 = 0.0
        valor_tabela_calculo = 0.0

        if valor_base < self.TABELA_SEGURO_DESEMPREGO[1]['valor']:
            valor_tabela_calculo = valor_base 
        else:
            valor_tabela_calculo = self.TABELA_SEGURO_DESEMPREGO[1]['valor']
        valor_parcial1 = valor_tabela_calculo * self.TABELA_SEGURO_DESEMPREGO[1]['percentual']

        if valor_tabela_calculo == self.TABELA_SEGURO_DESEMPREGO[1]['valor']:
            valor_parcial2 = valor_base - self.TABELA_SEGURO_DESEMPREGO[1]['valor']
        valor_parcial2 = valor_parcial2 * self.TABELA_SEGURO_DESEMPREGO[2]['percentual']
        
        total_parcial = valor_parcial1 + valor_parcial2

        if self.TABELA_SEGURO_DESEMPREGO['MINIMO_VIGENTE'] > total_parcial:
            resultado_parcial = self.TABELA_SEGURO_DESEMPREGO['MINIMO_VIGENTE']
        else:
            resultado_parcial = total_parcial

        if valor_base >= self.TABELA_SEGURO_DESEMPREGO['FIXO']['valor']:
            resultado = self.TABELA_SEGURO_DESEMPREGO['FIXO']['fixo']
        else:
            resultado = resultado_parcial

        return round(resultado, 2)
    
    def get_saldo_salario_quantidade(self):
        mes_ano_admissao = f'{self.mes_admissao:0>2}/{self.ano_admissao}'
        mes_ano_demissao = f'{self.mes_demissao:0>2}/{self.ano_demissao}'

        mesmo_mes_ano_admissao_demissao = True if mes_ano_admissao == mes_ano_demissao else False

        if mesmo_mes_ano_admissao_demissao:
            quantidade_de_dias = self.dia_demissao - self.dia_admissao
            return quantidade_de_dias
        return self.dia_demissao
    
    def get_salario_proporcional_13_qtde(self, salario_qtde):
        mesmo_ano_admissao_demissao = True if self.ano_admissao == self.ano_demissao else False
        data_proporcao = None
        if mesmo_ano_admissao_demissao:
            data_proporcao = self.data_admissao
        else:
            data_proporcao = datetime.datetime.strptime(f'01/01/{self.ano_demissao}', '%d/%m/%Y')

        mes_proporcao = data_proporcao.month
        mes_demissao = self.data_demissao.month
        
        if salario_qtde < 15:
            qtde_proporcional = (mes_demissao - 1) - mes_proporcao
        else:
            qtde_proporcional = mes_demissao - mes_proporcao        
        return qtde_proporcional + 1
    
    def get_ferias_proporcionais_qtde(self):
        if self.dia_demissao >= 15:
            qtde_dias_mes_demissao = calendar.monthrange(self.data_demissao.year, self.data_demissao.month)[-1]
        else:
            qtde_dias_mes_demissao = 1

        data_dia_mes_admissao__ano_dem = datetime.datetime.strptime(f'{self.dia_admissao}/{self.mes_admissao}/{self.ano_demissao}', '%d/%m/%Y')
        data_qtde_dias__mes_ano_demissao = datetime.datetime.strptime(f'{qtde_dias_mes_demissao}/{self.mes_demissao}/{self.ano_demissao}', '%d/%m/%Y')
        data_dia_mes_admissao__ano_anterior = data_dia_mes_admissao__ano_dem - datetime.timedelta(days=365)

        dia_mes_admissao_maior_que_dia_mes_demissao = data_dia_mes_admissao__ano_dem > data_qtde_dias__mes_ano_demissao

        if dia_mes_admissao_maior_que_dia_mes_demissao:
            result = data_qtde_dias__mes_ano_demissao - data_dia_mes_admissao__ano_anterior
        else:
            if (self.data_demissao - self.data_admissao).days > 365:
                result = data_qtde_dias__mes_ano_demissao - data_dia_mes_admissao__ano_dem
            else:
                result = data_qtde_dias__mes_ano_demissao - self.data_admissao

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
    
    def get_aviso_previo_inden_valor(self):
        salario_base_por_30 = (self.salario_base / 30)
        
        salario_base_mais_medias_he = (self.salario_base + self.medias_hora_extra)

        qtde_total_dias_registro = (self.data_demissao - self.data_admissao).days
        qtde_anos_resgistro = qtde_total_dias_registro / 365
        qtde_anos_arredondado_acima = math.floor(qtde_anos_resgistro)
        
        result = (salario_base_por_30 * (qtde_anos_arredondado_acima * 3)) + salario_base_mais_medias_he
        return result
    
    def get_valor_irrf(self, valor_base: float):
        resultado_parcial_irrf = valor_base * self.get_percentual_irrf(valor_base)
        deducao_irrf = self.get_deducao_irrf(valor_base)
        return round(resultado_parcial_irrf - deducao_irrf, 2)

    def get_numero_parcelas(self):
        meses_trabalhado = (self.data_demissao - self.data_admissao).days // 30
        if meses_trabalhado > 25:
            return self.MAPA_PARCELAS_SEGURO[25]
        return self.MAPA_PARCELAS_SEGURO[meses_trabalhado]
    
    def calcular(self):
        ################ Proventos ################

        lista_vencimentos = list()

        self.saldo_de_salario_qtde = self.get_saldo_salario_quantidade()
        self.saldo_de_salario_valor = round(self.salario_base / self.qtde_dias_mes * self.saldo_de_salario_qtde, 2)
        lista_vencimentos.append(self.saldo_de_salario_valor)

        self.salario_proporcional_13_qtde = self.get_salario_proporcional_13_qtde(self.saldo_de_salario_qtde)
        self.salario_proporcional_13_valor = (self.salario_base / 12) * self.salario_proporcional_13_qtde
        lista_vencimentos.append(self.salario_proporcional_13_valor)
        
        self.salario_variavel_13_qtde = self.get_salario_proporcional_13_qtde(self.saldo_de_salario_qtde)
        self.salario_variavel_13_valor = round((self.medias_hora_extra / 12) * self.salario_proporcional_13_qtde, 2)
        lista_vencimentos.append(self.salario_variavel_13_valor)

        if self.motivo != 1 or self.aviso_previo != 1:
            self.salario_indenizado_13_qtde = 0
            self.salario_indenizado_13_valor = 0
        else:
            self.salario_indenizado_13_qtde = 1
            self.salario_indenizado_13_valor = (self.salario_base + self.medias_hora_extra) / 12
        lista_vencimentos.append(self.salario_indenizado_13_valor)

        self.ferias_vencidas_qtde = None
        if self.ferias_vencidas == 1:
            self.ferias_vencidas_qtde = 0
        elif self.ferias_vencidas == 2:
            self.ferias_vencidas_qtde = 1
        elif self.ferias_vencidas == 3:
            self.ferias_vencidas_qtde = 3
        self.ferias_vencidas_valor = (self.salario_base + self.medias_hora_extra) * self.ferias_vencidas_qtde
        lista_vencimentos.append(self.ferias_vencidas_valor)

        self.ferias_proporcionais_qtde = self.get_ferias_proporcionais_qtde()
        self.ferias_proporcionais_valor = round((self.salario_base + self.medias_hora_extra) / 12 * self.ferias_proporcionais_qtde, 2)
        lista_vencimentos.append(self.ferias_proporcionais_valor)

        self.ferias_indenizadas_qtde = self.salario_indenizado_13_qtde
        self.ferias_indenizadas_valor = round(self.salario_indenizado_13_valor, 2)
        lista_vencimentos.append(self.ferias_indenizadas_valor)

        self.um_terco_sobre_ferias_qtde = '01/03'
        self.um_terco_sobre_ferias_valor = round(sum([self.ferias_vencidas_valor, self.ferias_proporcionais_valor, self.ferias_indenizadas_valor]) / 3, 2)
        lista_vencimentos.append(self.um_terco_sobre_ferias_valor)

        qtde_horas = int(self.horas_extras_quantidade)
        qtde_minutos = (self.horas_extras_quantidade - qtde_horas) * 100
        total_em_minutos = (qtde_horas * 60) + qtde_minutos
        resultado_total_he = total_em_minutos / 60

        self.horas_extras_50_valor = round(((self.salario_base / 220) + ((self.salario_base / 220) * self.horas_extras_percentual)) * resultado_total_he, 2)
        self.horas_extras_100_valor = round((self.salario_base / 220) * 2 * self.hora_extra_100, 2)
        lista_vencimentos.append(self.horas_extras_100_valor)

        self.aviso_previo_inden_qtde = 0
        self.aviso_previo_inden_valor = 0
        if self.aviso_previo == 1:
            self.aviso_previo_inden_qtde = 1
            self.aviso_previo_inden_valor = self.get_aviso_previo_inden_valor()
        lista_vencimentos.append(self.aviso_previo_inden_valor)

        self.total_vencimentos = round(sum(lista_vencimentos), 2)

        ################ Descontos ################
        lista_descontos = []
        lista_vencimento_base_calc_inss = [
            self.saldo_de_salario_valor,
            self.horas_extras_50_valor,
            self.horas_extras_100_valor,
            self.campo1_adicional_valor,
            self.campo2_adicional_valor,
        ]

        valor_base_calculo_inss = sum(lista_vencimento_base_calc_inss)
        valor_base_calculo_13 = sum([self.salario_proporcional_13_valor, self.salario_variavel_13_valor])

        self.inss_sobre_saldo_salario_qtde = self.get_percentual_contribuicao_inss(valor_base_calculo_inss)
        self.inss_sobre_saldo_salario_valor = self.get_valor_contribuicao_inss(valor_base_calculo_inss)
        lista_descontos.append(self.inss_sobre_saldo_salario_valor)

        qtde_horas = int(self.atrasos_faltas)
        qtde_minutos = (self.atrasos_faltas - qtde_horas) * 100
        total_em_minutos = (qtde_horas * 60) + qtde_minutos
        resultado_atrasos_faltas = total_em_minutos / 60

        self.atrasos_faltas_qtde = self.atrasos_faltas
        self.atrasos_faltas_valor = round(resultado_atrasos_faltas * (self.salario_base / 220), 2)
        lista_descontos.append(self.atrasos_faltas_valor)

        lista_vencimentos_base_calc_irrf = [
            self.saldo_de_salario_valor,
            self.horas_extras_50_valor,
            self.horas_extras_100_valor,
            self.aviso_previo_inden_valor,
            self.campo1_adicional_valor,
            self.campo2_adicional_valor,
        ]

        lista_vencimentos_13_base_calc_irrf = [
            self.salario_indenizado_13_valor,
            self.salario_variavel_13_valor,
            self.salario_proporcional_13_valor,
        ]

        valor_base_calculo_irrf = sum(lista_vencimentos_base_calc_irrf) - self.inss_sobre_saldo_salario_valor - self.atrasos_faltas_valor

        if self.dependentes > 5 :
            valor_base_calculo_irrf_sobre_13 = sum(lista_vencimentos_13_base_calc_irrf) - (5 * self.TABELA_IRRF[6][1])
        else:
            valor_base_calculo_irrf_sobre_13 = sum(lista_vencimentos_13_base_calc_irrf) - (self.dependentes * self.TABELA_IRRF[6][1])
        
        self.inss_sobre_salario_13_qtde = self.get_percentual_contribuicao_inss(valor_base_calculo_13)
        self.inss_sobre_salario_13_valor = self.get_valor_contribuicao_inss(valor_base_calculo_13)
        lista_descontos.append(self.inss_sobre_salario_13_valor)

        self.irrf_sobre_salario_qtde = self.get_percentual_irrf(valor_base_calculo_irrf)
        self.irrf_sobre_salario_valor = self.get_valor_irrf(valor_base_calculo_irrf)
        lista_descontos.append(self.irrf_sobre_salario_valor)

        self.irrf_sobre_salario_13_qtde = self.get_percentual_irrf(valor_base_calculo_irrf_sobre_13)
        self.irrf_sobre_salario_13_valor = self.get_valor_irrf(valor_base_calculo_irrf_sobre_13)
        lista_descontos.append(self.irrf_sobre_salario_13_valor)

        self.desconto_aviso_previo_qtde = 0
        self.desconto_aviso_previo_valor = 0.0
        if self.motivo == 2 and self.aviso_previo == 3:
            self.desconto_aviso_previo_qtde = 1
            self.desconto_aviso_previo_valor = self.salario_base + self.medias_hora_extra
        lista_descontos.append(self.desconto_aviso_previo_valor)
       
        self.adiantamentos_qtde = 0
        self.adiantamentos_valor = 0.0
        lista_descontos.append(self.adiantamentos_valor)

        self.total_descontos = round(sum(lista_descontos), 2)

        ################ LÍQUIDO DE RECISÃO ################
        self.liquido_de_rescisao = self.total_vencimentos - self.total_descontos

        ################ CÁLCULO DE MULTA DO FGTS ################
        lista_base_calculo_fgts_vencimento = [
            self.saldo_de_salario_valor,
            self.salario_proporcional_13_valor,
            self.salario_variavel_13_valor,
            self.horas_extras_50_valor,
            self.horas_extras_100_valor,
            self.campo1_adicional_valor,
            self.campo2_adicional_valor,
        ]

        valor_base_calculo_fgts_vencimento = sum(lista_base_calculo_fgts_vencimento)

        self.calculo_grrf = round(0.0 if self.motivo !=1 else self.fgts_depositado * self.grrf, 2)
        self.fgts_vencimentos = round(valor_base_calculo_fgts_vencimento * (8/100), 2)
        self.fgts_aviso_previo = round((self.aviso_previo_inden_valor + self.salario_indenizado_13_valor) * (8/100), 2)
        self.total_conta_fgts = round(sum([self.fgts_depositado, self.calculo_grrf * 80/100, self.fgts_vencimentos, self.fgts_aviso_previo]), 2)
        
        self.total_guia_grfc = sum([
            self.calculo_grrf,
            self.fgts_vencimentos,
            self.fgts_aviso_previo,
        ])
        
        ################ CÁLCULO DE MULTA DO FGTS ################
        valor_media_salarial_base_calculo = self.salario_base + self.medias_hora_extra

        self.media_salarial = 0.0 if self.motivo != 1 else valor_media_salarial_base_calculo
        self.numero_parcelas = 0 if self.motivo != 1 else self.get_numero_parcelas()
        self.valor_por_parcela = 0.0 if self.motivo != 1 and self.numero_parcelas == 0 else self.get_valor_por_parcela_seg(valor_media_salarial_base_calculo)
        self.total_seguro_desemprego = round(0.0 if self.motivo != 1 else self.numero_parcelas * self.valor_por_parcela, 2)

        self.resultado_da_rescisao = sum(
            [self.liquido_de_rescisao, self.total_guia_grfc, self.total_seguro_desemprego]
        )

        self.total_grf_parte_funcionario = round(sum([self.calculo_grrf*80/100, self.fgts_vencimentos, self.fgts_aviso_previo]), 2)

    def resumo(self):
        print('-' * 63)
        print('RESCISÃO:')
        print(f'{"VALOR LÍQUIDO DA RESCISÃO":.<50}', f'R$ {self.liquido_de_rescisao}')
        print()
        print('FUNDO DE GARANTIA:')
        print(f'{"TOTAL GRFC (SOMENTE A PARTE DO FUNCIONÁRIO):":.<50}', f'R$ {self.total_grf_parte_funcionario}')
        print(f'{"TOTAL DEPOSITADO NA CONTA DO FGTS:":.<50}', f'R$ {self.total_conta_fgts}')
        print()
        print('-' * 63)
        print('SEGURO DESEMPREGO (VALORES ESTIMADOS):')
        print(f'{"QUANTIDADE DE PARCELAS:":.<50}', f' {self.numero_parcelas}')
        print(f'{"VALOR POR PARCELA:":.<50}', f'R$ {self.valor_por_parcela}')
        print(f'{"TOTAL A RECEBER (SEGURO DESEMPREGO):":.<50}', f'R$ {self.total_seguro_desemprego}')
        print()
        print('-' * 63)
        print('VALOR TOTAL A RECEBER:')
        print(f'{"RESCISÃO":.<50}', f'R$ {self.liquido_de_rescisao}')
        print(f'{"MULTA FGTS:":.<50}', f'R$ {self.total_grf_parte_funcionario}')
        print(f'{"FGTS DEPOSITADO:":.<50}', f'R$ {self.fgts_depositado}')
        print(f'{"SEGURO DESEMPREGO:":.<50}', f'R$ {self.total_seguro_desemprego}')
        print('-' * 63)
        total_resumo = sum([
            self.liquido_de_rescisao,
            self.total_grf_parte_funcionario,
            self.fgts_depositado,
            self.total_seguro_desemprego,
        ])
        print(f'{"TOTAL A RECEBER:":.<50}', f'R$ {total_resumo}')


if '__main__' == __name__:

    rescisao = CalculoRescisao(
        qtde_dias_mes = 30,
        empresa = 'Empresa Teste',
        funcionario = 'Funcionario Teste',
        motivo = 1,
        data_admissao = datetime.datetime.strptime('01/01/2019', '%d/%m/%Y'),
        data_demissao = datetime.datetime.strptime('30/04/2020', '%d/%m/%Y'),
        salario_base = 2_500,
        medias_hora_extra = 0.0,
        aviso_previo = 1,
        ferias_vencidas = 1,
        horas_extras_percentual = 50/100,
        horas_extras_quantidade = 0.0,
        hora_extra_100 = 0.0,
        atrasos_faltas = 0.0,
        dependentes = 0,
        grrf = 40/100,
        fgts_depositado = 0.0,
    )

    rescisao.calcular()

    rescisao.resumo()

    
